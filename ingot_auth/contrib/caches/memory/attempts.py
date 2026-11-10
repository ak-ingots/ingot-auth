"""The attempts in memory."""

__all__ = ("AuthMemoryAttemptsCache",)

import datetime
import typing as t

from ingot_auth.methods import (
    AuthAttempt,
    AuthAttemptNotFoundError,
    BaseAuthAttemptsCache,
)

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryAttemptsCache(BaseAuthAttemptsCache):
    """
    The attempts in memory: an expired one is forgotten when it is taken, the
    time from :meth:`_get_now`.
    """

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._attempts: dict[str, AuthAttempt] = {}

    @t.override
    async def _put(self, attempt: AuthAttempt) -> None:
        self._attempts[attempt.id] = attempt

    @t.override
    async def _take(self, attempt_id: str) -> AuthAttempt:
        attempt = self._attempts.pop(attempt_id, None)
        if attempt is None or attempt.expires_at <= self._get_now():
            raise AuthAttemptNotFoundError.create()
        return attempt

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
