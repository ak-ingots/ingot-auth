"""The callers in Redis."""

__all__ = ("AuthRedisCallersCache",)

import datetime
import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.caches import AuthCaller, BaseAuthCallersCache

from .base import AuthRedisCacheMixin


class AuthRedisCallersCache(AuthRedisCacheMixin, BaseAuthCallersCache):
    """
    The callers in Redis, by the hashes of the tokens of their sessions and
    the digests of the groups they were formed by.
    """

    @t.override
    async def _get(self, token_hash: str, groups_digest: str) -> AuthCaller | None:
        key = self._redis_build_key("caller", token_hash, groups_digest)
        value = await self._redis_get(key)
        if value is None:
            return None
        return AuthCaller(
            uid=value["uid"],
            permissions=Permissions(value["permissions"]),
            is_root=value["is_root"],
            session_uid=value["session_uid"],
            profile_hash=value["profile_hash"],
        )

    @t.override
    async def _put(
        self,
        token_hash: str,
        groups_digest: str,
        caller: AuthCaller,
        expires_at: datetime.datetime,
    ) -> None:
        value = {
            "uid": caller.uid,
            "permissions": dict(caller.permissions),
            "is_root": caller.is_root,
            "session_uid": caller.session_uid,
            "profile_hash": caller.profile_hash,
        }
        key = self._redis_build_key("caller", token_hash, groups_digest)
        await self._redis_put(key, value, expires_at)

    @t.override
    async def _forget(self, token_hash: str, groups_digest: str) -> None:
        key = self._redis_build_key("caller", token_hash, groups_digest)
        await self._redis_forget(key)
