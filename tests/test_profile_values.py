import contextlib
import datetime
import decimal
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.storages.memory.profiles import (
    AuthMemoryAttrsStorage,
    AuthMemoryProfilesStorage,
    AuthMemoryTagsStorage,
)
from ingot_auth.profiles import (
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsParameters,
)
from ingot_auth.profiles.hashes import build_profile_hash
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import (
    AuthAttr,
    AuthAttrType,
    AuthAttrValue,
    AuthItemNotFoundError,
    AuthMembership,
    AuthProfile,
    AuthProfileNotFoundError,
    AuthProfileValues,
    AuthTag,
)
from tests import ANONYMOUS, QUIET, ROOT

NOW = datetime.datetime(2026, 11, 15, 12, tzinfo=datetime.UTC)


async def seed(project: AuthMemoryProject) -> None:
    profiles = project.auth.storage.profiles
    await profiles.create(AuthProfile(uid="a1", created_at=NOW))
    for tag_uid, name in ((1, "beta"), (2, "staff")):
        await profiles.tags.create(AuthTag(uid=tag_uid, name=name))
    for attr_uid, attr_type in enumerate(AuthAttrType, start=1):
        await profiles.attrs.create(
            AuthAttr(uid=attr_uid, name=attr_type.value, type=attr_type)
        )


class ProfileValuesTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = AuthMemoryProject()
        self.profiles = self.project.auth.profiles
        await seed(self.project)

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller = ROOT
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller)
        return await operations.runner.run(factory, parameters, metadata)

    async def test_an_operator_sets_the_tags_of_a_profile(self) -> None:
        parameters = AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset({2, 1}))
        for _ in range(2):  # run twice, it changes nothing more
            values = await self.run_operation(self.profiles.op_set_tags, parameters)
            self.assertEqual(values, AuthProfileValues(tag_uids=frozenset({1, 2})))
        none = AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset())
        values = await self.run_operation(self.profiles.op_set_tags, none)
        self.assertEqual(values, AuthProfileValues())

    async def test_an_operator_sets_the_values_of_a_profile(self) -> None:
        attr_values: dict[int, AuthAttrValue] = {
            1: True,
            2: 7,
            3: decimal.Decimal("1.50"),
            4: NOW,
            5: "Ann",
        }
        parameters = AuthSetProfileAttrValuesParameters(
            uid="a1", attr_values=attr_values
        )
        values = await self.run_operation(self.profiles.op_set_attr_values, parameters)
        self.assertEqual(values, AuthProfileValues(attr_values=attr_values))

    async def test_what_is_not_of_the_registries_is_refused(self) -> None:
        for factory, parameters, error in (
            (
                self.profiles.op_set_tags,
                AuthSetProfileTagsParameters(uid="b2", tag_uids=frozenset()),
                AuthProfileNotFoundError,
            ),
            (
                self.profiles.op_set_tags,
                AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset({1, 9})),
                AuthItemNotFoundError,
            ),
            (
                self.profiles.op_set_attr_values,
                AuthSetProfileAttrValuesParameters(uid="b2", attr_values={}),
                AuthProfileNotFoundError,
            ),
            (
                self.profiles.op_set_attr_values,
                AuthSetProfileAttrValuesParameters(uid="a1", attr_values={9: "x"}),
                AuthItemNotFoundError,
            ),
            (
                self.profiles.op_set_attr_values,
                AuthSetProfileAttrValuesParameters(uid="a1", attr_values={2: True}),
                AuthItemInvalidError,  # a bool is no int here
            ),
        ):
            with self.subTest(parameters=parameters):
                with self.assertRaises(error):
                    await self.run_operation(factory, parameters)
        values = await self.project.auth.storage.profiles.values.get("a1")
        self.assertEqual(values, AuthProfileValues())

    async def test_a_change_forgets_the_callers_of_the_profile(self) -> None:
        parameters = AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset({1}))
        with mock.patch.object(
            type(self.project.auth.sessions), "forget_callers"
        ) as forget:
            await self.run_operation(self.profiles.op_set_tags, parameters)
        forget.assert_awaited_once_with("a1")

    async def test_the_managers_may_set_them_the_user_not(self) -> None:
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.profiles.grp_managers", profile_uid="op")
        )
        sessions = self.project.auth.sessions
        parameters = AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset({1}))
        operator = await sessions.authenticate(
            (await sessions.open("op", "nickname", {})).token
        )
        await self.run_operation(self.profiles.op_set_tags, parameters, operator)
        user = await sessions.authenticate(
            (await sessions.open("a1", "nickname", {})).token
        )
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(self.profiles.op_set_tags, parameters, user)


class OwnProfileTestCase(ProfileValuesTestCase):
    async def test_a_user_reads_its_profile_and_its_hash(self) -> None:
        sessions = self.project.auth.sessions
        token = (await sessions.open("a1", "nickname", {})).token
        caller = await sessions.authenticate(token)
        tags = AuthSetProfileTagsParameters(uid="a1", tag_uids=frozenset({1}))
        await self.run_operation(self.profiles.op_set_tags, tags)
        changed = await sessions.authenticate(token)  # formed again
        self.assertNotEqual(changed.profile_hash, caller.profile_hash)
        profile = await self.run_operation(self.profiles.op_get_own, None, changed)
        self.assertEqual(
            (profile.tag_uids, profile.attr_values, profile.hash),
            (frozenset({1}), {}, changed.profile_hash),
        )
        self.assertEqual(profile.permissions, dict(changed.permissions))

    async def test_a_caller_of_no_profile_has_none(self) -> None:
        with self.assertRaises(AuthProfileNotFoundError):
            await self.run_operation(self.profiles.op_get_own, None, ROOT)
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(self.profiles.op_get_own, None, ANONYMOUS)


class SeededProfilesStorage(AuthMemoryProfilesStorage):
    def __init__(self) -> None:
        super().__init__()
        self._profiles["a1"] = AuthProfile(uid="a1", created_at=NOW)


class SeededTagsStorage(AuthMemoryTagsStorage):
    def __init__(self) -> None:
        super().__init__()
        self._items[1] = AuthTag(uid=1, name="beta")
        self._items[2] = AuthTag(uid=2, name="staff")


class SeededAttrsStorage(AuthMemoryAttrsStorage):
    def __init__(self) -> None:
        super().__init__()
        for attr_uid, attr_type in enumerate(AuthAttrType, start=1):
            self._items[attr_uid] = AuthAttr(
                uid=attr_uid, name=attr_type.value, type=attr_type
            )


class SeededAllProfilesStorage(SeededProfilesStorage):
    tags = Slot(SeededTagsStorage)
    attrs = Slot(SeededAttrsStorage)


class SeededStorage(AuthMemoryStorage):
    profiles = Slot(SeededAllProfilesStorage)


class SeededAuthUnit(AuthMemoryUnit):
    storage = Slot(SeededStorage)


class SeededProject(AuthMemoryProject):
    auth = Slot(SeededAuthUnit)


class CommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                code = CommandRunner(SeededProject, [*QUIET, *argv]).run()
            except SystemExit as error:  # argparse refuses what it cannot read
                code = int(error.code or 0)
        return code, out.getvalue()

    def test_the_tags_of_a_profile_are_set(self) -> None:
        self.assertEqual(
            self.run_project("auth", "profiles", "tags", "set", "a1", "2", "1"),
            (0, "tags\t1\t2\nattrs\n"),
        )

    def test_the_values_of_a_profile_are_read_by_their_types(self) -> None:
        self.assertEqual(
            self.run_project(
                "auth",
                "profiles",
                "attrs",
                "values",
                "set",
                "a1",
                "--value",
                "1=true",
                "--value",
                "2=7",
                "--value",
                "3=1.50",
                "--value",
                "4=2026-11-15T12:00:00+00:00",
                "--value",
                "5=Ann",
            ),
            (
                0,
                "tags\nattrs\t1=true\t2=7\t3=1.50\t4=2026-11-15T12:00:00+00:00"
                "\t5=Ann\n",
            ),
        )

    def test_a_value_not_of_its_type_is_refused(self) -> None:
        for value in ("1=yes", "2=seven", "3=NaN", "4=2026-11-15T12:00:00", "9=x"):
            with self.subTest(value=value):
                code, out = self.run_project(
                    "auth", "profiles", "attrs", "values", "set", "a1", "--value", value
                )
                self.assertEqual((code, out), (1, ""))

    def test_a_value_not_of_the_form_is_refused_by_the_parser(self) -> None:
        for value in ("1", "x=1"):
            with self.subTest(value=value):
                code, _ = self.run_project(
                    "auth", "profiles", "attrs", "values", "set", "a1", "--value", value
                )
                self.assertEqual(code, 2)


class ProfileHashTestCase(unittest.TestCase):
    def test_the_hash_changes_with_what_the_client_sees(self) -> None:
        values = AuthProfileValues(
            tag_uids=frozenset({1, 2}), attr_values={1: NOW, 2: 7}
        )
        known = build_profile_hash(values, {"shop": 1})
        same = AuthProfileValues(tag_uids=frozenset({2, 1}), attr_values={2: 7, 1: NOW})
        self.assertEqual(build_profile_hash(same, {"shop": 1}), known)
        for other, permissions in (
            (
                AuthProfileValues(tag_uids=frozenset({1}), attr_values={1: NOW, 2: 7}),
                {"shop": 1},
            ),
            (
                AuthProfileValues(
                    tag_uids=frozenset({1, 2}), attr_values={1: NOW, 2: "7"}
                ),
                {"shop": 1},
            ),
            (values, {"shop": 3}),
        ):
            with self.subTest(other=other, permissions=permissions):
                self.assertNotEqual(build_profile_hash(other, permissions), known)
