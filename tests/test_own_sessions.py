import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.sessions import (
    AuthOwnSessionNotFoundError,
    AuthRevokeOwnSessionParameters,
)
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionNotFoundError
from tests import ANONYMOUS, ROOT


class OwnSessionsTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = AuthMemoryProject()
        self.sessions = self.project.auth.sessions
        self.phone = await self.sessions.open("a1", "nickname", {1: "phone"})
        self.laptop = await self.sessions.open("a1", "nickname", {1: "laptop"})
        self.caller = await self.sessions.authenticate(self.laptop.token)

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller | None = None
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller or self.caller)
        return await operations.runner.run(factory, parameters, metadata)

    async def test_a_user_lists_its_open_sessions_the_current_marked(self) -> None:
        await self.sessions.open("b2", "nickname", {1: "another's"})
        own = await self.run_operation(self.sessions.op_list_own, None)
        self.assertEqual(
            [(s.uid, s.attr_values, s.is_current) for s in own],
            [
                (self.phone.session_uid, {1: "phone"}, False),
                (self.laptop.session_uid, {1: "laptop"}, True),
            ],
        )
        self.assertNotIn(self.laptop.token, repr(own))
        self.assertEqual(
            await self.run_operation(self.sessions.op_list_own, None, ROOT), ()
        )

    async def test_a_user_revokes_a_session_of_its_own(self) -> None:
        lost = AuthRevokeOwnSessionParameters(session_uid=self.phone.session_uid)
        await self.run_operation(self.sessions.op_revoke_own, lost)
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(self.phone.token)
        own = await self.run_operation(self.sessions.op_list_own, None)
        self.assertEqual([s.uid for s in own], [self.laptop.session_uid])
        storage = self.project.auth.storage
        assert isinstance(storage, AuthMemoryStorage)
        self.assertEqual(
            storage.sessions._sessions[self.phone.session_uid].close_reason,
            AuthSessionCloseReason.REVOKED,
        )

    async def test_a_session_of_another_or_closed_is_not_found(self) -> None:
        another = await self.sessions.open("b2", "nickname", {})
        lost = AuthRevokeOwnSessionParameters(session_uid=self.phone.session_uid)
        await self.run_operation(self.sessions.op_revoke_own, lost)
        for session_uid, caller in (
            (another.session_uid, self.caller),
            (self.phone.session_uid, self.caller),  # closed already
            ("unknown", self.caller),
            (self.laptop.session_uid, ROOT),  # the root has no session
        ):
            with self.subTest(session_uid=session_uid, caller=caller.uid):
                parameters = AuthRevokeOwnSessionParameters(session_uid=session_uid)
                with self.assertRaises(AuthOwnSessionNotFoundError) as error:
                    await self.run_operation(
                        self.sessions.op_revoke_own, parameters, caller
                    )
                self.assertEqual(error.exception.session_uid, session_uid)
        await self.sessions.authenticate(another.token)  # kept

    async def test_a_user_revokes_its_other_sessions(self) -> None:
        tablet = await self.sessions.open("a1", "nickname", {})
        count = await self.run_operation(self.sessions.op_revoke_others, None)
        self.assertEqual(count, 2)
        for token in (self.phone.token, tablet.token):
            with self.assertRaises(AuthSessionNotFoundError):
                await self.sessions.authenticate(token)
        await self.sessions.authenticate(self.laptop.token)  # the current one
        self.assertEqual(
            await self.run_operation(self.sessions.op_revoke_others, None, ROOT), 0
        )

    async def test_a_session_closed_meanwhile_is_not_counted(self) -> None:
        with mock.patch.object(
            type(self.sessions),
            "close",
            mock.AsyncMock(side_effect=AuthSessionNotFoundError.for_uid("x")),
        ):
            count = await self.run_operation(self.sessions.op_revoke_others, None)
        self.assertEqual(count, 0)

    async def test_the_anonymous_caller_may_not(self) -> None:
        lost = AuthRevokeOwnSessionParameters(session_uid=self.phone.session_uid)
        for factory, parameters in (
            (self.sessions.op_list_own, None),
            (self.sessions.op_revoke_own, lost),
            (self.sessions.op_revoke_others, None),
        ):
            with self.subTest(factory=factory):
                with self.assertRaises(OperationPermissionsError):
                    await self.run_operation(factory, parameters, ANONYMOUS)
