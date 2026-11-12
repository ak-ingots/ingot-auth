"""The contract of the storage of the sessions themselves."""

__all__ = ("AuthSessionsStorageContract",)

import datetime
import decimal

from ingot_auth.storages import (
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
)

from .base import BaseAuthContract
from .profiles import NOW


def create_session(
    session_id: str = "s1",
    token_hash: str = "h1",
    uid: str = "a1",
    opened_at: datetime.datetime = NOW,
) -> AuthSessionRecord:
    """An open session, its values one of each type."""
    return AuthSessionRecord(
        id=session_id,
        uid=uid,
        method="nickname",
        token_hash=token_hash,
        attr_values={1: True, 2: 7, 3: decimal.Decimal("1.50"), 4: NOW, 5: "iPhone"},
        opened_at=opened_at,
        seen_at=opened_at,
    )


class AuthSessionsStorageContract(BaseAuthContract):
    """
    The sessions of a storage: found open by the hash of the token, and by the
    uid of their profile.
    """

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

    async def test_the_open_sessions_of_a_profile_come_as_opened(self) -> None:
        sessions = self.project.auth.storage.sessions
        later = NOW + datetime.timedelta(hours=1)
        first = create_session("s3", "h3")
        second = create_session("s1", "h1", opened_at=later)
        for session in (second, create_session("s2", "h2", uid="b2"), first):
            await sessions.open(session)
        await sessions.open(create_session("s4", "h4"))
        await sessions.close("s4", AuthSessionCloseReason.SIGNED_OUT, later)
        self.assertEqual(await sessions.get_open("a1"), (first, second))
        self.assertEqual(await sessions.get_open("c3"), ())

    async def test_an_open_session_is_found_as_seen(self) -> None:
        sessions = self.project.auth.storage.sessions
        await sessions.open(create_session())
        await sessions.open(create_session("s2", "h2"))
        seen_at = NOW + datetime.timedelta(hours=1)
        await sessions.touch("s1", seen_at)
        self.assertEqual((await sessions.find("h1")).seen_at, seen_at)
        self.assertEqual((await sessions.get_open("a1"))[0].seen_at, seen_at)
        self.assertEqual((await sessions.find("h2")).seen_at, NOW)

    async def test_a_closed_session_is_not_seen(self) -> None:
        sessions = self.project.auth.storage.sessions
        await sessions.open(create_session())
        await sessions.close("s1", AuthSessionCloseReason.SIGNED_OUT, NOW)
        for session_id in ("s1", "s2"):
            with self.assertRaises(AuthSessionNotFoundError) as error:
                await sessions.touch(session_id, NOW)
            self.assertIn(session_id, str(error.exception))

    async def test_a_session_is_closed_once(self) -> None:
        sessions = self.project.auth.storage.sessions
        await sessions.open(create_session())
        reason = AuthSessionCloseReason.EXPIRED_ABSOLUTE
        await sessions.close("s1", reason, NOW)
        for session_id in ("s1", "s2"):
            with self.assertRaises(AuthSessionNotFoundError) as error:
                await sessions.close(session_id, reason, NOW)
            self.assertIn(session_id, str(error.exception))
