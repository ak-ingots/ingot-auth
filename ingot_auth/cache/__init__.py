"""
The cache of the auth: a facade for what lives minutes, not years, every part
of it abstract, which a backend in ``ingot_auth.contrib.caches`` implements.
"""

__all__ = ("AuthCache",)

from ingots.puer import Slot, Unit

from ingot_auth.methods import BaseAuthAttemptsCache
from ingot_auth.sessions import BaseAuthCallersCache, BaseAuthSessionsCache


class AuthCache(Unit):
    """
    The cache of the auth: a backend extends it with its own, and the project
    declares it in the slot of the auth.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    attempts = Slot(BaseAuthAttemptsCache)  # type: ignore[type-abstract]
    sessions = Slot(BaseAuthSessionsCache)  # type: ignore[type-abstract]
    callers = Slot(BaseAuthCallersCache)  # type: ignore[type-abstract]
