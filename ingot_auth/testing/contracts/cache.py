"""The contract of a cache: what a backend guarantees, whatever it runs on."""

__all__ = ("AuthAttemptsCacheContract",)

import asyncio
import datetime

from ingot_auth.methods import AuthAttempt, AuthAttemptNotFoundError

from .base import BaseAuthContract


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
            values={1: "iPhone"},
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
