"""The callers of the sessions in memory."""

__all__ = ("AuthMemoryCallersCache",)

import datetime
import typing as t

from ingot_auth.caches import AuthCaller, BaseAuthCallersCache

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryCallersCache(BaseAuthCallersCache):
    """
    The callers in memory, each with the time it expires at: an expired one is
    forgotten when it is got, the time from :meth:`_get_now`.
    """

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._callers: dict[str, tuple[AuthCaller, datetime.datetime]] = {}

    @t.override
    async def _get(self, token_hash: str) -> AuthCaller | None:
        try:
            caller, expires_at = self._callers[token_hash]
        except KeyError:
            return None
        if expires_at <= self._get_now():
            del self._callers[token_hash]
            return None
        return caller

    @t.override
    async def _put(
        self, token_hash: str, caller: AuthCaller, expires_at: datetime.datetime
    ) -> None:
        self._callers[token_hash] = (caller, expires_at)

    @t.override
    async def _forget(self, token_hash: str) -> None:
        self._callers.pop(token_hash, None)

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
