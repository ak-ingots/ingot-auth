"""The sessions in Redis."""

__all__ = ("AuthRedisSessionsCache",)

import datetime
import typing as t

from ingot_auth.caches import BaseAuthSessionsCache
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionRecord

from .base import AuthRedisCacheMixin
from .values import (
    build_attr_values,
    build_json_attr_values,
    build_json_time,
    build_time,
)


class AuthRedisSessionsCache(AuthRedisCacheMixin, BaseAuthSessionsCache):
    """The sessions in Redis, by the hashes of their tokens."""

    @t.override
    async def _get(self, token_hash: str) -> AuthSessionRecord | None:
        value = await self._redis_get(self._redis_build_key("session", token_hash))
        if value is None:
            return None
        closed_at, close_reason = value["closed_at"], value["close_reason"]
        return AuthSessionRecord(
            uid=value["uid"],
            profile_uid=value["profile_uid"],
            method=value["method"],
            token_hash=token_hash,
            attr_values=build_attr_values(value["attr_values"]),
            opened_at=build_time(value["opened_at"]),
            seen_at=build_time(value["seen_at"]),
            closed_at=None if closed_at is None else build_time(closed_at),
            close_reason=(
                None if close_reason is None else AuthSessionCloseReason(close_reason)
            ),
        )

    @t.override
    async def _put(
        self, session: AuthSessionRecord, expires_at: datetime.datetime
    ) -> None:
        closed_at = session.closed_at
        value = {
            "uid": session.uid,
            "profile_uid": session.profile_uid,
            "method": session.method,
            "attr_values": build_json_attr_values(session.attr_values),
            "opened_at": build_json_time(session.opened_at),
            "seen_at": build_json_time(session.seen_at),
            "closed_at": None if closed_at is None else build_json_time(closed_at),
            "close_reason": session.close_reason,
        }
        key = self._redis_build_key("session", session.token_hash)
        await self._redis_put(key, value, expires_at)

    @t.override
    async def _forget(self, token_hash: str) -> None:
        await self._redis_forget(self._redis_build_key("session", token_hash))
