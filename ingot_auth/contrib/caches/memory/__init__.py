"""
The cache in memory: for the tests and the addon run on its own, or a
project of one process. An application declares it in the slot of its auth:
``cache = Slot(AuthMemoryCache)``.
"""

__all__ = (
    "AuthMemoryAttemptsCache",
    "AuthMemoryCache",
    "AuthMemoryCallersCache",
    "AuthMemorySessionsCache",
)

from ingots.puer import Slot

from ingot_auth.caches import AuthCache

from .attempts import AuthMemoryAttemptsCache
from .callers import AuthMemoryCallersCache
from .sessions import AuthMemorySessionsCache


class AuthMemoryCache(AuthCache):
    """The cache of the auth in memory."""

    attempts = Slot(AuthMemoryAttemptsCache)
    sessions = Slot(AuthMemorySessionsCache)
    callers = Slot(AuthMemoryCallersCache)
