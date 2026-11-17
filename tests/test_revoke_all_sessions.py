import contextlib
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.activities import AuthListActivitiesParameters
from ingot_auth.sessions import (
    AuthListSessionsParameters,
    AuthRevokeAllSessionsParameters,
)
from ingot_auth.storages import (
    AuthActivityAction,
    AuthMembership,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)
from tests import QUIET
from tests.test_sessions_record import SeededProject


class RevokeAllTestCase(unittest.IsolatedAsyncioTestCase):
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

    async def caller_of(self, uid: str) -> Caller:
        opened = await self.sessions.open(uid, "nickname", {})
        return await self.sessions.authenticate(opened.token)

    async def test_every_open_session_of_a_profile_is_revoked(self) -> None:
        phone = await self.sessions.open("a1", "nickname", {})
        laptop = await self.sessions.open("a1", "nickname", {})
        other = await self.sessions.open("b1", "nickname", {})
        await self.sessions.authenticate(phone.token)  # cached
        parameters = AuthRevokeAllSessionsParameters(profile_uid="a1")
        count = await self.run_operation(
            self.sessions.op_revoke_all, parameters, self.operator
        )
        self.assertEqual(count, 2)
        for token in (phone.token, laptop.token):
            with self.assertRaises(AuthSessionNotFoundError):
                await self.sessions.authenticate(token)
        await self.sessions.authenticate(other.token)  # another's kept
        record = await self.run_operation(
            self.sessions.op_list,
            AuthListSessionsParameters(profile_uid="a1", closed=True),
            self.operator,
        )
        self.assertEqual(
            {s.close_reason for s in record}, {AuthSessionCloseReason.REVOKED}
        )
        query = AuthListActivitiesParameters(action=AuthActivityAction.REVOKE)
        revoked = await self.project.auth.storage.activities.find(query)
        self.assertEqual(
            sorted((r.who, r.entity_uid) for r in revoked),
            sorted(("op", s.session_uid) for s in (phone, laptop)),
        )
        # none left, none of an unknown profile
        self.assertEqual(
            await self.run_operation(
                self.sessions.op_revoke_all, parameters, self.operator
            ),
            0,
        )
        nobody = AuthRevokeAllSessionsParameters(profile_uid="nobody")
        self.assertEqual(
            await self.run_operation(
                self.sessions.op_revoke_all, nobody, self.operator
            ),
            0,
        )

    async def test_a_session_closed_meanwhile_is_not_counted(self) -> None:
        await self.sessions.open("a1", "nickname", {})
        parameters = AuthRevokeAllSessionsParameters(profile_uid="a1")
        with mock.patch.object(
            type(self.sessions),
            "close",
            mock.AsyncMock(side_effect=AuthSessionNotFoundError.for_uid("x")),
        ):
            count = await self.run_operation(
                self.sessions.op_revoke_all, parameters, self.operator
            )
        self.assertEqual(count, 0)

    async def test_the_user_may_not(self) -> None:
        user = await self.caller_of("a1")
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(
                self.sessions.op_revoke_all,
                AuthRevokeAllSessionsParameters(profile_uid="a1"),
                user,
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

    def test_the_count_revoked_is_printed(self) -> None:
        self.assertEqual(
            self.run_project("auth", "sessions", "revoke-all", "a1"), (0, "1\n")
        )
