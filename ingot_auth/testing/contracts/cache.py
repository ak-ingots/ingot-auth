"""The contract of a cache: what a backend guarantees, whatever it runs on."""

__all__ = (
    "AuthAttemptsCacheContract",
    "AuthCallersCacheContract",
    "AuthSessionsCacheContract",
)

import asyncio
import datetime
import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.access.groups import AuthGroupsPermissions
from ingot_auth.caches import AuthAttempt, AuthAttemptNotFoundError, AuthCaller

from .base import BaseAuthContract
from .sessions import create_session

CALLER: t.Final = AuthCaller(
    uid="a1",
    session_id="s1",
    permissions=Permissions(AuthGroupsPermissions.CAN_READ),
)


class AuthAttemptsCacheContract(BaseAuthContract):
    """
    The attempts of a cache. A state of a method is kept as it is given; a
    cache that is not in the process tells which states it keeps.
    """

    def create_attempt(
        self, attempt_id: str = "x", expires_in: float = 60, failures: int = 0
    ) -> AuthAttempt:
        """An attempt expiring in ``expires_in`` seconds."""
        now = datetime.datetime.now(datetime.UTC)
        return AuthAttempt(
            id=attempt_id,
            flow="sign_up",
            method="testing",
            state="state",
            attr_values={1: "iPhone"},
            expires_at=now + datetime.timedelta(seconds=expires_in),
            failures=failures,
        )

    async def test_an_attempt_is_taken_as_put(self) -> None:
        attempts = self.project.auth.cache.attempts
        attempt = self.create_attempt()
        await attempts.put(attempt)
        self.assertEqual(await attempts.take("x"), attempt)

    async def test_an_attempt_is_taken_once(self) -> None:
        attempts = self.project.auth.cache.attempts
        await attempts.put(self.create_attempt())
        await attempts.take("x")
        with self.assertRaises(AuthAttemptNotFoundError):
            await attempts.take("x")

    async def test_an_unknown_attempt_is_not_found(self) -> None:
        with self.assertRaises(AuthAttemptNotFoundError):
            await self.project.auth.cache.attempts.take("x")

    async def test_an_expired_attempt_is_not_found(self) -> None:
        attempts = self.project.auth.cache.attempts
        await attempts.put(self.create_attempt(expires_in=-1))
        with self.assertRaises(AuthAttemptNotFoundError):
            await attempts.take("x")

    async def test_putting_again_replaces_it(self) -> None:
        attempts = self.project.auth.cache.attempts
        await attempts.put(self.create_attempt())
        again = self.create_attempt(failures=1)
        await attempts.put(again)
        self.assertEqual(await attempts.take("x"), again)

    async def test_of_concurrent_takes_one_wins(self) -> None:
        attempts = self.project.auth.cache.attempts
        await attempts.put(self.create_attempt())
        results = await asyncio.gather(
            attempts.take("x"), attempts.take("x"), return_exceptions=True
        )
        taken = [r for r in results if isinstance(r, AuthAttempt)]
        self.assertEqual(len(taken), 1, results)


class AuthSessionsCacheContract(BaseAuthContract):
    """The sessions of a cache, by the hashes of their tokens."""

    async def test_a_session_is_got_as_put(self) -> None:
        sessions = self.project.auth.cache.sessions
        session = create_session()
        await sessions.put(session, in_seconds(60))
        self.assertEqual(await sessions.get("h1"), session)

    async def test_a_session_missed_is_none(self) -> None:
        sessions = self.project.auth.cache.sessions
        await sessions.put(create_session(), in_seconds(60))
        self.assertIsNone(await sessions.get("h2"))

    async def test_an_expired_session_is_none(self) -> None:
        sessions = self.project.auth.cache.sessions
        await sessions.put(create_session(), in_seconds(-1))
        self.assertIsNone(await sessions.get("h1"))

    async def test_a_forgotten_session_is_none(self) -> None:
        sessions = self.project.auth.cache.sessions
        await sessions.put(create_session(), in_seconds(60))
        await sessions.forget("h1")
        await sessions.forget("h2")
        self.assertIsNone(await sessions.get("h1"))


class AuthCallersCacheContract(BaseAuthContract):
    """The callers of a cache, by the hashes of the tokens of their sessions."""

    async def test_a_caller_is_got_as_put(self) -> None:
        callers = self.project.auth.cache.callers
        await callers.put("h1", CALLER, in_seconds(60))
        self.assertEqual(await callers.get("h1"), CALLER)

    async def test_a_caller_missed_is_none(self) -> None:
        callers = self.project.auth.cache.callers
        await callers.put("h1", CALLER, in_seconds(60))
        self.assertIsNone(await callers.get("h2"))

    async def test_an_expired_caller_is_none(self) -> None:
        callers = self.project.auth.cache.callers
        await callers.put("h1", CALLER, in_seconds(-1))
        self.assertIsNone(await callers.get("h1"))

    async def test_a_forgotten_caller_is_none(self) -> None:
        callers = self.project.auth.cache.callers
        await callers.put("h1", CALLER, in_seconds(60))
        await callers.forget("h1")
        await callers.forget("h2")
        self.assertIsNone(await callers.get("h1"))


def in_seconds(seconds: float) -> datetime.datetime:
    """The time in that many seconds."""
    return datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=seconds)
