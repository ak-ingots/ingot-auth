"""
The methods of signing up and in, and the frame they run in: a method
verifies in steps, a challenge asking for an answer or the verified subject,
and an attempt keeps a flow between its steps. The core binds no method: its
methods, one subpackage each, ``nickname`` and ``email_code``, are a
catalogue an application takes from, declaring those it takes as slots of
:class:`AuthMethodsUnit`::

    class AppMethods(AuthMethodsUnit):
        nickname = Slot(AuthNicknameMethod)
"""

__all__ = (
    "AuthAttempt",
    "AuthAttemptNotFoundError",
    "AuthChallenge",
    "AuthMethodError",
    "AuthMethodInvalidError",
    "AuthMethodNotFoundError",
    "AuthMethodRefusedError",
    "AuthMethodUnsupportedError",
    "AuthMethodsUnit",
    "AuthStep",
    "AuthVerified",
    "BaseAuthAttemptsCache",
    "BaseAuthMethod",
)

import typing as t

from ingots.puer import Slot, Unit

from .attempts import AuthAttempt, BaseAuthAttemptsCache
from .base import BaseAuthMethod
from .errors import (
    AuthAttemptNotFoundError,
    AuthMethodError,
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodUnsupportedError,
)
from .password import AuthPassword
from .steps import AuthChallenge, AuthStep, AuthVerified


class AuthMethodsUnit(Unit):
    """
    The methods of the project, none here: a subclass declares each as a
    slot, the name of the slot the name of the method. The password of a
    profile, which the methods of a password share, is the slot ``password``,
    not a method.
    """

    password = Slot(AuthPassword)

    @t.final
    def get_all(self) -> tuple[BaseAuthMethod[t.Any, t.Any, t.Any], ...]:
        """The methods, in the order of their slots."""
        return tuple(
            self.slots_find_entity(name, BaseAuthMethod)
            for name, _ in type(self).slots_iter(BaseAuthMethod)
        )

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
