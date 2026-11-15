import datetime
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.activities import AuthListActivitiesParameters
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.profiles import (
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsParameters,
)
from ingot_auth.sessions import AuthRevokeOwnSessionParameters
from ingot_auth.sign_in import AuthSignedIn, AuthStartSignInParameters
from ingot_auth.sign_up import AuthSignedUp, AuthStartSignUpParameters
from ingot_auth.storages import (
    AuthActivityAction,
    AuthAttr,
    AuthAttrType,
    AuthMembership,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    AuthTag,
)
from ingot_auth.sessions.presets.operations import AuthUnbindSessionAttrParameters
from ingot_auth.testing.methods import AuthTestingMethod, AuthTestingStart
from tests import ROOT


class TstMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class ActivityRecordsTestCase(unittest.IsolatedAsyncioTestCase):
    """Each change of state of the core recorded, by its action and context."""

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.auth = self.project.auth

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller = ROOT
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller, run_uid="r1")
        return await operations.runner.run(factory, parameters, metadata)

    async def last(self, count: int = 1) -> t.Any:
        query = AuthListActivitiesParameters(limit=count)
        return await self.auth.storage.activities.find(query)

    async def sign_up_and_in(self) -> tuple[str, AuthSignedIn]:
        anonymous = self.project.operations.callers.get_anonymous()
        start = AuthTestingStart(subject="a@b.c")
        signed_up = await self.run_operation(
            self.auth.sign_up.op_start,
            AuthStartSignUpParameters(method="testing", parameters=start),
            anonymous,
        )
        assert isinstance(signed_up, AuthSignedUp)
        signed_in = await self.run_operation(
            self.auth.sign_in.op_start,
            AuthStartSignInParameters(method="testing", parameters=start),
            anonymous,
        )
        assert isinstance(signed_in, AuthSignedIn)
        return signed_up.uid, signed_in

    async def test_the_sign_up_and_the_sign_in_are_recorded(self) -> None:
        uid, signed_in = await self.sign_up_and_in()
        sign_in, bound, created = await self.last(3)
        self.assertEqual(
            [(r.who, r.action, r.entity_type, r.entity_id) for r in (created, bound)],
            [
                ("anonymous", AuthActivityAction.CREATE, "auth.profiles", uid),
                ("anonymous", AuthActivityAction.BIND, "auth.profiles", uid),
            ],
        )
        self.assertEqual(
            (created.context, bound.context),
            ({"method": "testing", "identifier_kind": "testing"}, {"kind": "testing"}),
        )
        self.assertEqual(
            (sign_in.action, sign_in.entity_type, sign_in.entity_id, sign_in.context),
            (
                AuthActivityAction.SIGN_IN,
                "auth.sessions",
                signed_in.session_id,
                {"uid": uid, "method": "testing"},
            ),
        )

    async def test_the_end_of_the_sessions_is_recorded(self) -> None:
        uid, signed_in = await self.sign_up_and_in()
        sessions = self.auth.sessions
        caller = await sessions.authenticate(signed_in.token)
        other = await sessions.open(uid, "testing", {})
        another = await sessions.open(uid, "testing", {})
        await self.run_operation(
            sessions.op_revoke_own,
            AuthRevokeOwnSessionParameters(session_id=other.session_id),
            caller,
        )
        await self.run_operation(sessions.op_revoke_others, None, caller)
        await self.run_operation(self.auth.sign_out.op_sign_out, None, caller)
        sign_out, revoke_others, revoke_own = await self.last(3)
        self.assertEqual(
            [(r.action, r.entity_id) for r in (revoke_own, revoke_others, sign_out)],
            [
                (AuthActivityAction.REVOKE, other.session_id),
                (AuthActivityAction.REVOKE, another.session_id),
                (AuthActivityAction.SIGN_OUT, signed_in.session_id),
            ],
        )
        self.assertEqual(
            {(r.who, r.session_id) for r in (sign_out, revoke_own)},
            {(uid, signed_in.session_id)},
        )

    async def test_a_session_expiring_is_recorded_by_the_server(self) -> None:
        uid, signed_in = await self.sign_up_and_in()
        sessions = self.auth.sessions
        later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=31)
        with (
            mock.patch.object(type(sessions), "_get_now", return_value=later),
            self.assertLogs("ingot_auth.sessions", "INFO") as logs,
        ):
            with self.assertRaises(Exception):
                await sessions.authenticate(signed_in.token)
        (expired,) = await self.last()
        self.assertEqual(
            (expired.who, expired.session_id, expired.action, expired.context),
            (
                "system",
                None,
                AuthActivityAction.EXPIRE,
                {"reason": "expired_absolute"},
            ),
        )
        self.assertIn(expired.run_uid, logs.output[0])

    async def test_the_members_and_the_presets_are_recorded(self) -> None:
        uid, _ = await self.sign_up_and_in()
        members = self.auth.access.members
        membership = AuthMembership(group="auth.profiles.grp_managers", uid=uid)
        await self.run_operation(members.op_add, membership)
        await self.run_operation(members.op_remove, membership)
        presets = self.auth.sessions.presets
        await self.run_operation(
            self.auth.sessions.attrs.op_create,
            AuthSessionAttr(
                id=1,
                name="device",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.CLIENT,
            ),
        )
        await self.run_operation(presets.op_create, AuthSessionPreset(id=1, name="web"))
        await self.run_operation(
            presets.op_bind,
            AuthSessionPresetBinding(preset_id=1, attr_id=1, required=False),
        )
        await self.run_operation(
            presets.op_unbind, AuthUnbindSessionAttrParameters(preset_id=1, attr_id=1)
        )
        unbind, bind, _, _, unbound, bound = await self.last(6)
        self.assertEqual(
            [
                (r.action, r.entity_type, r.entity_id, r.context)
                for r in (bound, unbound)
            ],
            [
                (
                    AuthActivityAction.BIND,
                    "auth.access.members",
                    uid,
                    {"group": "auth.profiles.grp_managers"},
                ),
                (
                    AuthActivityAction.UNBIND,
                    "auth.access.members",
                    uid,
                    {"group": "auth.profiles.grp_managers"},
                ),
            ],
        )
        self.assertEqual(
            [(r.action, r.entity_type, r.entity_id, r.context) for r in (bind, unbind)],
            [
                (
                    AuthActivityAction.BIND,
                    "auth.sessions.presets",
                    "1",
                    {"attr_id": 1, "required": False},
                ),
                (
                    AuthActivityAction.UNBIND,
                    "auth.sessions.presets",
                    "1",
                    {"attr_id": 1},
                ),
            ],
        )

    async def test_the_values_of_a_profile_are_recorded(self) -> None:
        uid, _ = await self.sign_up_and_in()
        storage = self.auth.storage.profiles
        await storage.tags.create(AuthTag(id=1, name="beta"))
        await storage.attrs.create(AuthAttr(id=2, name="name", type=AuthAttrType.STR))
        profiles = self.auth.profiles
        await self.run_operation(
            profiles.op_set_tags,
            AuthSetProfileTagsParameters(uid=uid, tag_ids=frozenset({1})),
        )
        await self.run_operation(
            profiles.op_set_attr_values,
            AuthSetProfileAttrValuesParameters(uid=uid, attr_values={2: "Ann"}),
        )
        values, tags = await self.last(2)
        self.assertEqual(
            [(r.action, r.entity_type, r.entity_id, r.context) for r in (tags, values)],
            [
                (AuthActivityAction.UPDATE, "auth.profiles", uid, {"tag_ids": [1]}),
                (
                    AuthActivityAction.UPDATE,
                    "auth.profiles",
                    uid,
                    {"attr_values": {"2": "Ann"}},
                ),
            ],
        )
