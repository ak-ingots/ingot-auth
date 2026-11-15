import contextlib
import dataclasses
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemorySessionsUnit
from ingot_auth.activities import (
    AuthActivitiesUnit,
    AuthActivityContext,
    AuthListActivitiesParameters,
    AuthSwallowActivityFailure,
)
from ingot_auth.auth import AuthUnit
from ingot_auth.caches import AuthCaller
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import (
    AuthMemoryActivitiesStorage,
    AuthMemoryStorage,
)
from ingot_auth.project import AuthProject
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.storages import (
    AuthActivityAction,
    AuthAttr,
    AuthAttrType,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthTag,
)
from ingot_auth.testing.contracts.activities import create_record
from tests import ROOT, masks


class SwallowActivitiesUnit(AuthActivitiesUnit):
    failure = Slot(AuthSwallowActivityFailure)


# the log of the auth in memory is strict, which no swallowing extends: an
# auth in memory of its own, swallowing
class SwallowAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)
    activities = Slot(SwallowActivitiesUnit)


class SwallowProject(AuthProject):
    auth = Slot(SwallowAuthUnit)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ManyKindsSet(AuthActivityContext):
    tag_uids: frozenset[int]
    attr_uids: tuple[int, ...]
    values: dict[str, list[int]]


class ActivitiesTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project: AuthProject = AuthMemoryProject()

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller = ROOT
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller, run_uid="r1")
        return await operations.runner.run(factory, parameters, metadata)

    async def find(self, **filters: t.Any) -> t.Any:
        query = AuthListActivitiesParameters(**filters)
        return await self.project.auth.storage.activities.find(query)

    async def test_a_registry_records_its_changes(self) -> None:
        auth = self.project.auth
        tags = auth.profiles.tags
        caller = AuthCaller(
            uid="op",
            session_uid="s9",
            permissions=masks(*tags.permissions.flags),
            profile_hash="h",
        )
        await self.run_operation(tags.op_create, AuthTag(uid=1, name="beta"), caller)
        await self.run_operation(
            tags.op_rename, AuthRenameItemParameters(uid=1, name="staff"), caller
        )
        await self.run_operation(
            tags.op_delete, AuthDeleteItemParameters(uid=1), caller
        )
        records = await self.find()
        self.assertEqual(
            [(r.action, r.entity_type, r.entity_uid, r.context) for r in records],
            [
                (AuthActivityAction.DELETE, "auth.profiles.tags", "1", {}),
                (
                    AuthActivityAction.UPDATE,
                    "auth.profiles.tags",
                    "1",
                    {"name": "staff"},
                ),
                (AuthActivityAction.CREATE, "auth.profiles.tags", "1", {}),
            ],
        )
        self.assertEqual(
            {(r.who, r.session_uid, r.run_uid) for r in records}, {("op", "s9", "r1")}
        )

    async def test_an_attribute_created_tells_what_it_is(self) -> None:
        auth = self.project.auth
        await self.run_operation(
            auth.profiles.attrs.op_create,
            AuthAttr(uid=1, name="first_name", type=AuthAttrType.STR),
        )
        await self.run_operation(
            auth.sessions.attrs.op_create,
            AuthSessionAttr(
                uid=1,
                name="ip",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.TRANSPORT,
            ),
        )
        session_attr, profile_attr = await self.find()
        self.assertEqual(
            (profile_attr.entity_type, profile_attr.context),
            ("auth.profiles.attrs", {"name": "first_name", "type": "str"}),
        )
        self.assertEqual(
            (session_attr.who, session_attr.session_uid, session_attr.context),
            ("root", None, {"name": "ip", "type": "str", "source": "transport"}),
        )

    async def test_a_context_is_kept_as_plain_values(self) -> None:
        auth = self.project.auth
        metadata = self.project.operations.create_metadata(ROOT, run_uid="r1")
        context = ManyKindsSet(
            tag_uids=frozenset({3, 1}), attr_uids=(2, 1), values={"a": [1]}
        )
        await auth.activities.record(
            auth.profiles, "a1", AuthActivityAction.UPDATE, metadata, context=context
        )
        (record,) = await self.find()
        self.assertEqual(
            record.context,
            {"tag_uids": [1, 3], "attr_uids": [2, 1], "values": {"a": [1]}},
        )

    async def test_a_strict_log_fails_the_change_with_it(self) -> None:
        tags = self.project.auth.profiles.tags
        with mock.patch.object(
            AuthMemoryActivitiesStorage, "_append", side_effect=OSError("gone")
        ):
            with self.assertRaises(OSError):
                await self.run_operation(tags.op_create, AuthTag(uid=1, name="beta"))
        self.assertEqual(await self.project.auth.storage.profiles.tags.get_all(), ())

    async def test_a_swallowed_failure_lets_the_change_through(self) -> None:
        self.project = SwallowProject()
        tags = self.project.auth.profiles.tags
        with (
            mock.patch.object(
                AuthMemoryActivitiesStorage, "_append", side_effect=OSError("gone")
            ),
            self.assertLogs("ingot_auth.activities.failures", "ERROR") as logs,
        ):
            await self.run_operation(tags.op_create, AuthTag(uid=1, name="beta"))
        self.assertEqual(
            len(await self.project.auth.storage.profiles.tags.get_all()), 1
        )
        self.assertEqual(await self.find(), ())
        self.assertIn("is not recorded", logs.output[0])

    async def test_the_auditors_read_the_log_the_others_not(self) -> None:
        auth = self.project.auth
        await self.run_operation(
            auth.profiles.tags.op_create, AuthTag(uid=1, name="beta")
        )
        auditor = Caller(
            uid="au", permissions=auth.activities.grp_auditors.get_permissions()
        )
        query = AuthListActivitiesParameters(entity_type="auth.profiles.tags")
        records = await self.run_operation(auth.activities.op_list, query, auditor)
        self.assertEqual([r.entity_uid for r in records], ["1"])
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(auth.activities.op_list, query, Caller(uid="a1"))


class CommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))
        self.enterContext(mock.patch("logging.config.dictConfig"))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            try:
                code = CommandRunner(
                    AuthMemoryProject, ["--config", "IS_PRINT_CONFIGS=off", *argv]
                ).run()
            except SystemExit as error:  # argparse refuses what it cannot read
                code = int(error.code or 0)
        return code, out.getvalue()

    def test_the_activities_are_printed(self) -> None:
        with mock.patch.object(
            AuthMemoryActivitiesStorage, "_find", autospec=True
        ) as find:
            find.return_value = (
                create_record(session_uid="s1", context={"ids": [1, 3]}),
                create_record(),
            )
            code, out = self.run_project(
                "auth",
                "activities",
                "list",
                "--entity",
                "auth.profiles:a1",
                "--who",
                "root",
                "--session",
                "s1",
                "--action",
                "update",
                "--since",
                "2026-11-15T00:00:00+00:00",
                "--until",
                "2026-11-16T00:00:00+00:00",
                "--limit",
                "5",
            )
        when = "2026-11-02T09:30:15.123000+00:00"
        self.assertEqual(
            (code, out),
            (
                0,
                f"{when}\troot\ts1\tcreate\tauth.profiles.tags\t1\tr1\tids=[1, 3]\n"
                f"{when}\troot\t-\tcreate\tauth.profiles.tags\t1\tr1\n",
            ),
        )
        query = find.call_args.args[1]
        self.assertEqual(
            (query.entity_type, query.entity_uid, query.who, query.session_uid),
            ("auth.profiles", "a1", "root", "s1"),
        )
        self.assertEqual((query.action, query.limit), (AuthActivityAction.UPDATE, 5))

    def test_a_time_with_no_offset_is_refused(self) -> None:
        code, _ = self.run_project(
            "auth", "activities", "list", "--since", "2026-11-15T00:00:00"
        )
        self.assertEqual(code, 2)
