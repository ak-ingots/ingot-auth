import datetime
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionNotFoundError
from tests import ANONYMOUS, ROOT


class SignOutTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = AuthMemoryProject()
        self.sessions = self.project.auth.sessions

    async def sign_out(self, caller: Caller) -> None:
        operations = self.project.operations
        metadata = operations.create_metadata(caller)
        await operations.runner.run(
            self.project.auth.sign_out.op_sign_out, None, metadata
        )

    def get_close_reason(self, session_id: str) -> AuthSessionCloseReason | None:
        storage = self.project.auth.storage
        assert isinstance(storage, AuthMemoryStorage)
        return storage.sessions._sessions[session_id].close_reason

    async def test_a_caller_signs_out_its_token_working_no_more(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        kept = await self.sessions.open("a1", "nickname", {})
        caller = await self.sessions.authenticate(opened.token)  # cached now
        await self.sign_out(caller)
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(opened.token)
        self.assertEqual(
            self.get_close_reason(opened.session_id),
            AuthSessionCloseReason.SIGNED_OUT,
        )
        self.assertEqual(
            (await self.sessions.authenticate(kept.token)).uid, "a1"
        )  # another session of the profile stays open

    async def test_a_caller_of_no_session_signs_out_of_nothing(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        for caller in (ROOT, ANONYMOUS):
            with self.subTest(caller=caller):
                await self.sign_out(caller)
        self.assertIsNone(self.get_close_reason(opened.session_id))

    async def test_a_session_closed_meanwhile_signs_out_of_nothing(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        caller = await self.sessions.authenticate(opened.token)
        await self.sign_out(caller)
        await self.sign_out(caller)  # the cached caller of a closed session

    async def test_a_session_closed_by_another_request_is_forgotten(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        await self.sessions.authenticate(opened.token)  # cached now
        storage = self.project.auth.storage.sessions
        stale = await storage.get_open("a1")
        now = datetime.datetime.now(datetime.UTC)
        await storage.close(opened.session_id, AuthSessionCloseReason.REVOKED, now)
        with mock.patch.object(
            type(storage), "get_open", mock.AsyncMock(return_value=stale)
        ):
            await self.sessions.close(
                "a1",
                opened.session_id,
                AuthSessionCloseReason.SIGNED_OUT,
                closed_by="a1",
            )
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(opened.token)
        self.assertEqual(
            self.get_close_reason(opened.session_id), AuthSessionCloseReason.REVOKED
        )

    async def test_a_session_of_another_profile_is_not_found(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.close(
                "b2",
                opened.session_id,
                AuthSessionCloseReason.SIGNED_OUT,
                closed_by="b2",
            )
        self.assertIsNone(self.get_close_reason(opened.session_id))
