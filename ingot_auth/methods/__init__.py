"""
The methods of signing up and in, and the frame they run in: a method
verifies in steps, a challenge asking for an answer or the verified subject,
and an attempt keeps a flow between its steps. The core assumes no method:
an application declares those it takes as slots of :class:`AuthMethods`::

    class AppMethods(AuthMethods):
        password = Slot(AppPasswordMethod)
"""

__all__ = (
    "AuthAttempt",
    "AuthAttemptNotFoundError",
    "AuthChallenge",
    "AuthMethodError",
    "AuthMethodNotFoundError",
    "AuthMethodRefusedError",
    "AuthMethodUnsupportedError",
    "AuthMethods",
    "AuthStep",
    "AuthVerified",
    "BaseAuthAttemptsCache",
    "BaseAuthMethod",
)

import typing as t

from ingots.puer import Unit

from .attempts import AuthAttempt, BaseAuthAttemptsCache
from .base import BaseAuthMethod
from .errors import (
    AuthAttemptNotFoundError,
    AuthMethodError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodUnsupportedError,
)
from .steps import AuthChallenge, AuthStep, AuthVerified


class AuthMethods(Unit):
    """
    The methods of the project, none here: a subclass declares each as a
    slot, the name of the slot the name of the method.
    """

    @t.final
    def get(self, name: str) -> BaseAuthMethod[t.Any, t.Any, t.Any]:
        """
        The method of a name.

        :raises AuthMethodNotFoundError: no slot of a method has the name.
        """
        try:
            return self.slots_find_entity(name, BaseAuthMethod)
        except LookupError:
            raise AuthMethodNotFoundError.for_name(name) from None
