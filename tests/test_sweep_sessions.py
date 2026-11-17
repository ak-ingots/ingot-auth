import contextlib
import datetime
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.activities import AuthActivitiesUnit, AuthListActivitiesParameters
from ingot_auth.caches import AuthCaller
from ingot_auth.sessions import AuthSessionsUnit, AuthSweepSessionsParameters
from ingot_auth.storages import (
    AuthActivityAction,
    AuthMembership,
    AuthSessionNotFoundError,
)
from tests import QUIET
from tests.test_sessions_record import SeededProject

LATER = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=31)


class SweepTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = AuthMemoryProject()
        self.sessions = self.project.auth.sessions
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.sessions.grp_admins", profile_uid="op")
        )
        self.operator = await self.caller_of("op")

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller)
        return await operations.runner.run(factory, parameters, metadata)

    async def caller_of(self, uid: str) -> AuthCaller:
        opened = await self.sessions.open(uid, "nickname", {})
        return await self.sessions.authenticate(opened.token)

    def sweep_later(self, page_size: int = 2) -> t.Any:
        parameters = AuthSweepSessionsParameters(page_size=page_size)
        return self.run_operation(self.sessions.op_sweep, parameters, self.operator)

    async def test_the_expired_sessions_are_closed_a_page_at_a_time(self) -> None:
        old = [await self.sessions.open(uid, "nickname", {}) for uid in "aab"]
        await self.sessions.authenticate(old[0].token)  # cached
        with mock.patch.object(AuthSessionsUnit, "_get_now", return_value=LATER):
            fresh = await self.sessions.open("a", "nickname", {})
            # the operator's own session expired too: it is no request
            self.assertEqual(await self.sweep_later(), 4)
            for opened in old:
                with self.assertRaises(AuthSessionNotFoundError):
                    await self.sessions.authenticate(opened.token)
            await self.sessions.authenticate(fresh.token)  # lives
            self.assertEqual(await self.sweep_later(), 0)  # none left
        query = AuthListActivitiesParameters(action=AuthActivityAction.EXPIRE)
        expired = await self.project.auth.storage.activities.find(query)
        self.assertEqual(
            sorted((r.who, r.entity_uid, dict(r.context)) for r in expired),
            sorted(
                ("op", uid, {"reason": "expired_absolute"})
                for uid in (*(o.session_uid for o in old), self.operator.session_uid)
            ),
        )

    async def test_nothing_expired_closes_none(self) -> None:
        await self.sessions.open("a", "nickname", {})
        self.assertEqual(
            await self.run_operation(
                self.sessions.op_sweep, AuthSweepSessionsParameters(), self.operator
            ),
            0,
        )

    async def test_a_session_closed_meanwhile_is_not_counted(self) -> None:
        storage = self.project.auth.storage.sessions
        with (
            mock.patch.object(AuthSessionsUnit, "_get_now", return_value=LATER),
            mock.patch.object(
                type(storage),
                "_close",
                mock.AsyncMock(side_effect=AuthSessionNotFoundError.for_uid("x")),
            ),
        ):
            self.assertEqual(await self.sweep_later(), 0)
        query = AuthListActivitiesParameters(action=AuthActivityAction.EXPIRE)
        self.assertEqual(await self.project.auth.storage.activities.find(query), ())

    async def test_the_user_may_not(self) -> None:
        user = await self.caller_of("a")
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(
                self.sessions.op_sweep, AuthSweepSessionsParameters(), user
            )


class CommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(SeededProject, [*QUIET, *argv]).run()
        return code, out.getvalue()

    def test_a_job_sweeps_as_the_auth_system(self) -> None:
        with (
            mock.patch.object(AuthSessionsUnit, "_get_now", return_value=LATER),
            mock.patch.object(AuthActivitiesUnit, "record", autospec=True) as record,
        ):
            self.assertEqual(self.run_project("auth", "sessions", "sweep"), (0, "1\n"))
        (call,) = record.call_args_list
        _, _, entity_uid, action, metadata = call.args
        self.assertEqual(
            (entity_uid, action, metadata.caller.uid),
            ("s3", AuthActivityAction.EXPIRE, "auth.system"),
        )
