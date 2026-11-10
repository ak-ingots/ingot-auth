"""The contract of the storage of the sessions themselves."""

__all__ = ("AuthSessionsStorageContract",)

import datetime
import decimal

from ingot_auth.sessions import (
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
)

from .base import BaseAuthContract
from .profiles import NOW


def create_session(session_id: str = "s1", token_hash: str = "h1") -> AuthSessionRecord:
    """An open session, its values one of each type."""
    return AuthSessionRecord(
        id=session_id,
        uid="a1",
        method="nickname",
        token_hash=token_hash,
        values={1: True, 2: 7, 3: decimal.Decimal("1.50"), 4: NOW, 5: "iPhone"},
        opened_at=NOW,
    )


class AuthSessionsStorageContract(BaseAuthContract):
    """The sessions of a storage: found open by the hash of the token."""

    async def test_an_open_session_is_found_as_opened(self) -> None:
        sessions = self.project.auth.storage.sessions
        session = create_session()
        await sessions.open(session)
        await sessions.open(create_session("s2", "h2"))
        self.assertEqual(await sessions.find("h1"), session)

    async def test_an_unknown_hash_is_not_found(self) -> None:
        await self.project.auth.storage.sessions.open(create_session())
        with self.assertRaises(AuthSessionNotFoundError):
            await self.project.auth.storage.sessions.find("h2")

    async def test_a_closed_session_is_not_found(self) -> None:
        sessions = self.project.auth.storage.sessions
        await sessions.open(create_session())
        await sessions.open(create_session("s2", "h2"))
        closed_at = NOW + datetime.timedelta(hours=1)
        await sessions.close("s1", AuthSessionCloseReason.EXPIRED_ABSOLUTE, closed_at)
        with self.assertRaises(AuthSessionNotFoundError):
            await sessions.find("h1")
        self.assertEqual((await sessions.find("h2")).id, "s2")

    async def test_a_session_is_closed_once(self) -> None:
        sessions = self.project.auth.storage.sessions
        await sessions.open(create_session())
        reason = AuthSessionCloseReason.EXPIRED_ABSOLUTE
        await sessions.close("s1", reason, NOW)
        for session_id in ("s1", "s2"):
            with self.assertRaises(AuthSessionNotFoundError) as error:
                await sessions.close(session_id, reason, NOW)
            self.assertIn(session_id, str(error.exception))
