"""The sessions in memory."""

__all__ = ("AuthMemorySessionsCache",)

import datetime
import typing as t

from ingot_auth.sessions import BaseAuthSessionsCache
from ingot_auth.storages import AuthSessionRecord

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemorySessionsCache(BaseAuthSessionsCache):
    """
    The sessions in memory, each with the time it expires at: an expired one is
    forgotten when it is got, the time from :meth:`_get_now`.
    """

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._sessions: dict[str, tuple[AuthSessionRecord, datetime.datetime]] = {}

    @t.override
    async def _get(self, token_hash: str) -> AuthSessionRecord | None:
        try:
            session, expires_at = self._sessions[token_hash]
        except KeyError:
            return None
        if expires_at <= self._get_now():
            del self._sessions[token_hash]
            return None
        return session

    @t.override
    async def _put(
        self, session: AuthSessionRecord, expires_at: datetime.datetime
    ) -> None:
        self._sessions[session.token_hash] = (session, expires_at)

    @t.override
    async def _forget(self, token_hash: str) -> None:
        self._sessions.pop(token_hash, None)

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
