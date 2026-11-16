"""A part of the cache in Redis."""

__all__ = ("AuthRedisCacheMixin",)

import datetime
import json
import typing as t

if t.TYPE_CHECKING:
    from ingot_redis import RedisProject
    from ingot_redis.redis.clients import BaseRedisClient


class AuthRedisCacheMixin:
    """
    A part of the cache in Redis, on a client of ingot-redis: a value is JSON
    under a key of :attr:`REDIS_PREFIX`, expiring at its time.
    """

    # the first part of every key, so that the auth shares a database
    REDIS_PREFIX: t.ClassVar[str] = "ingot_auth"

    project: "RedisProject"

    @t.final
    def _redis_build_key(self, *parts: str) -> str:
        return ":".join((self.REDIS_PREFIX, *parts))

    @t.final
    async def _redis_put(
        self, key: str, value: object, expires_at: datetime.datetime
    ) -> None:
        """Keeps a value until the time, in place of one of the key."""
        client = await self._redis_get_client()
        pxat = int(expires_at.timestamp() * 1000)
        await client.client.set(key, json.dumps(value), pxat=pxat)

    @t.final
    async def _redis_get(self, key: str) -> t.Any:
        """The value of the key, ``None`` if missed or expired."""
        client = await self._redis_get_client()
        data = await client.client.get(key)
        return None if data is None else json.loads(data)

    @t.final
    async def _redis_take(self, key: str) -> t.Any:
        """The value of the key, forgotten at once, ``None`` if missed or expired."""
        client = await self._redis_get_client()
        data = await client.client.getdel(key)
        return None if data is None else json.loads(data)

    @t.final
    async def _redis_forget(self, key: str) -> None:
        client = await self._redis_get_client()
        await client.client.delete(key)

    def _redis_get_client(self) -> "BaseRedisClient":
        """The client of the cache: another one is a matter of an override."""
        return self.project.redis.clients.default
