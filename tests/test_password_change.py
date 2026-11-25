"""The change of a password by its user, its event and its mail."""

import typing as t
import unittest
from unittest import mock

from ingot_mail.contrib.memory import MemoryMailer
from ingots.defaults.operations import (
    BaseOperation,
    Caller,
    OperationMetadata,
    OperationPermissionsError,
    Permissions,
)
from ingots.puer import Factories, Slot

from ingot_auth.caches import AuthCaller
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.methods import AuthMethodInvalidError
from ingot_auth.methods.password import (
    AuthChangePasswordParameters,
    AuthPasswordChanged,
    AuthPasswordRefusedError,
)
from ingot_auth.storages import (
    AuthActivityAction,
    AuthActivityQuery,
    AuthAttrType,
    AuthIdentity,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)
from tests import ANONYMOUS, ROOT
from tests.test_password import TstAuthUnit, TstMethodsUnit, TstPassword, TstProject

OLD: t.Final = "correct horse battery staple"
NEW: t.Final = "another horse battery staple"


class AuditOperation(BaseOperation[AuthPasswordChanged, None]):
    """A subscriber of the application beside the mail."""

    project: "AuditProject"

    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()

    @t.override
    async def _run(
        self, parameters: AuthPasswordChanged, metadata: OperationMetadata
    ) -> None:
        self.project.seen.append(parameters)


class AuditPassword(TstPassword):
    # the mail dropped, the audit alone
    ev_changed = Factories[BaseOperation[AuthPasswordChanged, None]](AuditOperation)


class AuditMethods(TstMethodsUnit):
    password = Slot(AuditPassword)


class AuditAuth(TstAuthUnit):
    methods = Slot(AuditMethods)


class AuditProject(TstProject):
    auth = Slot(AuditAuth)

    def __init__(self) -> None:
        super().__init__()
        self.seen: list[AuthPasswordChanged] = []


class ChangePasswordTestCase(unittest.IsolatedAsyncioTestCase):
    project: TstProject

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        await self.set_up(TstProject())

    async def set_up(self, project: TstProject) -> None:
        self.project = project
        auth = project.auth
        storage = auth.storage
        await storage.sessions.attrs.create(
            AuthSessionAttr(
                uid=1,
                name="device",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.CLIENT,
            )
        )
        for kind, value in (("email", "alice@example.com"), ("nickname", "alice")):
            await storage.profiles.identities.create(
                AuthIdentity(kind=kind, value=value, profile_uid="a1")
            )
        await storage.profiles.secrets.put("a1", await auth.methods.password.hash(OLD))
        self.phone = await auth.sessions.open("a1", "nickname", {1: "a phone"})
        self.laptop = await auth.sessions.open("a1", "nickname", {1: "a laptop"})
        caller = await auth.sessions.authenticate(self.laptop.token)
        assert isinstance(caller, AuthCaller)
        self.caller = caller

    async def change(
        self, old: str = OLD, new: str = NEW, caller: Caller | None = None
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller or self.caller)
        return await operations.run(
            self.project.auth.methods.password.op_change,
            AuthChangePasswordParameters(old=old, new=new),
            metadata,
        )

    def get_sent(self) -> tuple[t.Any, ...]:
        mailer = self.project.mail.mailer
        assert isinstance(mailer, MemoryMailer)
        return mailer.get_sent()

    async def test_a_user_changes_its_password_and_is_told(self) -> None:
        result = await self.change()
        self.assertEqual(self.get_sent(), ())  # the reply first, the mail after
        self.assertEqual(result.revoked, 1)
        password = self.project.auth.methods.password
        self.assertTrue(await password.verify(NEW, "a1"))
        self.assertFalse(await password.verify(OLD, "a1"))
        await self.project.events.join()
        [mail] = self.get_sent()
        self.assertEqual(mail.to, ("alice@example.com",))
        self.assertIn("device a laptop", mail.text)
        self.assertNotIn(NEW, mail.text)
        self.assertNotIn(OLD, mail.text)

    async def test_the_other_sessions_are_closed_this_one_kept(self) -> None:
        await self.change()
        sessions = self.project.auth.sessions
        with self.assertRaises(AuthSessionNotFoundError):
            await sessions.authenticate(self.phone.token)
        await sessions.authenticate(self.laptop.token)
        storage = self.project.auth.storage
        assert isinstance(storage, AuthMemoryStorage)
        self.assertEqual(
            storage.sessions._sessions[self.phone.session_uid].close_reason,
            AuthSessionCloseReason.REVOKED,
        )

    async def test_the_change_and_the_closes_are_recorded(self) -> None:
        await self.change()
        records = await self.project.auth.storage.activities.find(
            AuthActivityQuery(who="a1")
        )
        self.assertCountEqual(
            [(r.entity_type, r.entity_uid, r.action) for r in records],
            [
                ("auth.methods.password", "a1", AuthActivityAction.UPDATE),
                ("auth.sessions", self.phone.session_uid, AuthActivityAction.REVOKE),
            ],
        )

    async def test_a_wrong_old_password_is_refused(self) -> None:
        with self.assertRaises(AuthPasswordRefusedError):
            await self.change(old="a wrong old password")
        await self.assert_unchanged()

    async def test_a_new_one_breaking_the_policies_is_refused(self) -> None:
        with self.assertRaises(AuthMethodInvalidError) as error:
            await self.change(new="short")
        self.assertEqual(
            (error.exception.field, error.exception.policies), ("password", ("length",))
        )
        await self.assert_unchanged()

    async def test_a_profile_with_no_password_is_refused(self) -> None:
        caller = await self.project.auth.sessions.authenticate(
            (await self.project.auth.sessions.open("b2", "nickname", {})).token
        )
        with self.assertRaises(AuthPasswordRefusedError):
            await self.change(caller=caller)

    async def test_a_caller_of_no_session_is_refused(self) -> None:
        with self.assertRaises(AuthPasswordRefusedError):
            await self.change(caller=ROOT)
        with self.assertRaises(OperationPermissionsError):
            await self.change(caller=ANONYMOUS)

    async def test_a_password_changed_meanwhile_is_refused(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        original = secrets.replace

        async def changed_meanwhile(uid: str, old: str, new: str) -> None:
            await secrets.put(uid, "changed by another request")
            await original(uid, old, new)

        with mock.patch.object(secrets, "replace", changed_meanwhile):
            with self.assertRaises(AuthPasswordRefusedError):
                await self.change()
        await self.project.events.join()
        self.assertEqual(self.get_sent(), ())
        await self.project.auth.sessions.authenticate(self.phone.token)

    async def test_a_session_closed_meanwhile_is_not_counted(self) -> None:
        sessions = self.project.auth.sessions
        gone = AuthSessionNotFoundError.for_uid(self.phone.session_uid)
        with mock.patch.object(sessions, "close", side_effect=gone):
            result = await self.change()
        self.assertEqual(result.revoked, 0)

    async def test_a_profile_of_no_email_is_told_by_no_mail(self) -> None:
        storage = self.project.auth.storage
        assert isinstance(storage, AuthMemoryStorage)
        del storage.profiles.identities._uids["email", "alice@example.com"]
        await self.change()
        await self.project.events.join()
        self.assertEqual(self.get_sent(), ())

    async def test_an_application_takes_the_event_its_own_way(self) -> None:
        project = AuditProject()
        await self.set_up(project)
        await self.change()
        await project.events.join()
        self.assertEqual(self.get_sent(), ())
        [event] = project.seen
        self.assertEqual(
            (event.profile_uid, event.session_uid, dict(event.session_attr_values)),
            ("a1", self.laptop.session_uid, {"device": "a laptop"}),
        )

    async def assert_unchanged(self) -> None:
        self.assertTrue(await self.project.auth.methods.password.verify(OLD, "a1"))
        await self.project.auth.sessions.authenticate(self.phone.token)
        await self.project.events.join()
        self.assertEqual(self.get_sent(), ())
