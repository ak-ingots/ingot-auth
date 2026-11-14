"""
The sign-up: a method verifies who it is, in steps, and the sign-up creates
the profile, binds the subject of the method to it and keeps the record of
what it happened on. It opens no session. It is open by its toggle,
``AUTH_SIGN_UP_ENABLED``, on by default, by every method: closed, it closes
the sign-up of each method too.
"""

__all__ = (
    "AuthAnswerSignUpOperation",
    "AuthAnswerSignUpParameters",
    "AuthSignUpChallenge",
    "AuthSignUpPermissions",
    "AuthSignUpResult",
    "AuthSignUpUnit",
    "AuthSignedUp",
    "AuthStartSignUpOperation",
    "AuthStartSignUpParameters",
)

import typing as t

from ingots.defaults.operations import OperationsOwner, Permissions, PermissionsSlot
from ingots.puer import Factory, Unit

from .items import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from .operations import AuthAnswerSignUpOperation, AuthStartSignUpOperation
from .permissions import AuthSignUpPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthSignUpUnit(OperationsOwner, Unit):
    """
    The operations of the sign-up, a start and the answers to it, open by
    the toggle of :meth:`_get_enabled`.
    """

    project: "AuthProject"

    permissions = PermissionsSlot(AuthSignUpPermissions)

    op_start = Factory(AuthStartSignUpOperation)
    op_answer = Factory(AuthAnswerSignUpOperation)

    @t.final
    def get_enabled(self) -> bool:
        """Whether the sign-up is open in the project, by every method."""
        return self._get_enabled()

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """
        What the sign-up gives the anonymous caller, by its toggle: its
        ``CAN_SIGN_UP`` while it is open.
        """
        if self.get_enabled():
            return self.permissions(self.permissions.flags.CAN_SIGN_UP)
        return Permissions()

    def _get_enabled(self) -> bool:
        """The toggle of the configs, ``AUTH_SIGN_UP_ENABLED``."""
        return self.project.settings.configs.AUTH_SIGN_UP_ENABLED
