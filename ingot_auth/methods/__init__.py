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
    "AuthChallenge",
    "AuthMethodDeniedError",
    "AuthMethodError",
    "AuthMethodInvalidError",
    "AuthMethodNotFoundError",
    "AuthMethodRefusedError",
    "AuthMethodUnsupportedError",
    "AuthMethodsUnit",
    "AuthStep",
    "AuthVerified",
    "BaseAuthFlowOperation",
    "BaseAuthMethod",
)

import typing as t

from ingots.defaults.operations import Permissions
from ingots.puer import Slot, Unit

from .base import BaseAuthMethod
from .errors import (
    AuthMethodDeniedError,
    AuthMethodError,
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodUnsupportedError,
)
from .operations import BaseAuthFlowOperation
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

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """
        What the methods give the anonymous caller, by their toggles: the
        flags of the sign-up and of the sign-in of each method that opens
        them. Those of the flows themselves, of every method, are of the
        server, ``AuthSignUpPermissions.CAN_SIGN_UP``.
        """
        permissions = Permissions()
        for method in self.get_all():
            if method.get_sign_up_enabled():
                permissions |= method.get_sign_up_permissions()
            if method.get_sign_in_enabled():
                permissions |= method.get_sign_in_permissions()
        return permissions

    @t.final
    def get_signed_in_permissions(self) -> Permissions:
        """
        What the methods give a signed-in user, by their toggles: the flag
        of the sign-in of each method that opens it, which a sign-in checks
        the profile has once the method found it.
        """
        permissions = Permissions()
        for method in self.get_all():
            if method.get_sign_in_enabled():
                permissions |= method.get_sign_in_permissions()
        return permissions
