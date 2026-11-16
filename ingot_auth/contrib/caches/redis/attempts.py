"""The attempts in Redis."""

__all__ = ("AuthRedisAttemptsCache",)

import typing as t

from ingot_auth.caches import (
    AuthAttempt,
    AuthAttemptNotFoundError,
    BaseAuthAttemptsCache,
)

from .base import AuthRedisCacheMixin
from .values import (
    build_attr_values,
    build_json_attr_values,
    build_json_time,
    build_time,
)

if t.TYPE_CHECKING:
    from ingot_auth.methods import BaseAuthMethod
    from ingot_auth.project import AuthProject


class AuthRedisAttemptsCache(AuthRedisCacheMixin, BaseAuthAttemptsCache):
    """
    The attempts in Redis, by their ids: taken by ``GETDEL``, so two takes of
    one never both have it; its state given as plain values by its method,
    found by name in the methods of the auth.
    """

    @t.override
    async def _put(self, attempt: AuthAttempt) -> None:
        method = self._redis_get_method(attempt.method)
        value = {
            "flow": attempt.flow,
            "method": attempt.method,
            "state": method.dump_state(attempt.state),
            "attr_values": build_json_attr_values(attempt.attr_values),
            "expires_at": build_json_time(attempt.expires_at),
            "failures": attempt.failures,
        }
        key = self._redis_build_key("attempt", attempt.uid)
        await self._redis_put(key, value, attempt.expires_at)

    @t.override
    async def _take(self, attempt_uid: str) -> AuthAttempt:
        value = await self._redis_take(self._redis_build_key("attempt", attempt_uid))
        if value is None:
            raise AuthAttemptNotFoundError.create()
        method = self._redis_get_method(value["method"])
        return AuthAttempt(
            uid=attempt_uid,
            flow=value["flow"],
            method=value["method"],
            state=method.load_state(value["state"]),
            attr_values=build_attr_values(value["attr_values"]),
            expires_at=build_time(value["expires_at"]),
            failures=value["failures"],
        )

    @t.final
    def _redis_get_method(self, name: str) -> "BaseAuthMethod[t.Any, t.Any, t.Any]":
        # a part of the cache of the auth is in a project of the auth
        return t.cast("AuthProject", self.project).auth.methods.get(name)
