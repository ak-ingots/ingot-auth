"""
The cache in Redis, under the extra ``redis``, on the client of ingot-redis:
for a project of more than one process, which share it. An application
declares it in the slot of its auth, ``cache = Slot(AuthRedisCache)``, and
joins the ``RedisProject`` of ingot-redis. What it keeps is JSON of plain
values, never pickled, under keys of the prefix ``ingot_auth``, each
expiring at its time; the state of an attempt is given as plain values by
its method.
"""

__all__ = (
    "AuthRedisAttemptsCache",
    "AuthRedisCache",
    "AuthRedisCacheMixin",
    "AuthRedisCallersCache",
    "AuthRedisSessionsCache",
)

from ingots.puer import Slot

from ingot_auth.caches import AuthCache

from .attempts import AuthRedisAttemptsCache
from .base import AuthRedisCacheMixin
from .callers import AuthRedisCallersCache
from .sessions import AuthRedisSessionsCache


class AuthRedisCache(AuthCache):
    """The cache of the auth in Redis."""

    attempts = Slot(AuthRedisAttemptsCache)
    sessions = Slot(AuthRedisSessionsCache)
    callers = Slot(AuthRedisCallersCache)
