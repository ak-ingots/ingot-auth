"""
The caches of the auth: the interfaces a backend in ``ingot_auth.contrib.caches``
implements, for what lives minutes, not years, with what they keep and what
they raise, depending on no other part of the auth than the storages, whose
records they keep too. :class:`AuthCache` is the facade.
"""

__all__ = (
    "AuthAttempt",
    "AuthAttemptNotFoundError",
    "AuthCache",
    "AuthCaller",
    "BaseAuthAttemptsCache",
    "BaseAuthCallersCache",
    "BaseAuthSessionsCache",
)

from ingots.puer import Slot, Unit

from .attempts import BaseAuthAttemptsCache
from .callers import BaseAuthCallersCache
from .errors import AuthAttemptNotFoundError
from .items import AuthAttempt, AuthCaller
from .sessions import BaseAuthSessionsCache


class AuthCache(Unit):
    """
    The cache of the auth, every part of it abstract: a backend extends it
    with its own, and the project declares it in the slot of the auth.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    attempts = Slot(BaseAuthAttemptsCache)  # type: ignore[type-abstract]
    sessions = Slot(BaseAuthSessionsCache)  # type: ignore[type-abstract]
    callers = Slot(BaseAuthCallersCache)  # type: ignore[type-abstract]
