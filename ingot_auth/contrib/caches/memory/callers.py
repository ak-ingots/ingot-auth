"""The callers of the sessions in memory."""

__all__ = ("AuthMemoryCallersCache",)

import datetime
import typing as t

from ingot_auth.caches import AuthCaller, BaseAuthCallersCache


class AuthMemoryCallersCache(BaseAuthCallersCache):
    """
    The callers in memory, each with the time it expires at: an expired one is
    forgotten when it is got, the time from :meth:`_get_now`.
    """

    def __init__(self) -> None:
        super().__init__()
        self._callers: dict[tuple[str, str], tuple[AuthCaller, datetime.datetime]] = {}

    @t.override
    async def _get(self, token_hash: str, groups_digest: str) -> AuthCaller | None:
        key = (token_hash, groups_digest)
        try:
            caller, expires_at = self._callers[key]
        except KeyError:
            return None
        if expires_at <= self._get_now():
            del self._callers[key]
            return None
        return caller

    @t.override
    async def _put(
        self,
        token_hash: str,
        groups_digest: str,
        caller: AuthCaller,
        expires_at: datetime.datetime,
    ) -> None:
        self._callers[token_hash, groups_digest] = (caller, expires_at)

    @t.override
    async def _forget(self, token_hash: str, groups_digest: str) -> None:
        self._callers.pop((token_hash, groups_digest), None)

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)
