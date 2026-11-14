"""
The sign-in: a method verifies who it is, in steps, and the sign-in finds the
profile bound to what the method verified, checks the profile may sign in by
the method and opens a session of it, giving its token. A step replies no
sooner than the strategy of its timing says, the slot ``timing``, none by
default, which a project declares.
"""

__all__ = (
    "AuthAnswerSignInOperation",
    "AuthAnswerSignInParameters",
    "AuthFloorTiming",
    "AuthNoTiming",
    "AuthSignInChallenge",
    "AuthSignInPermissions",
    "AuthSignInResult",
    "AuthSignInUnit",
    "AuthSignedIn",
    "AuthStartSignInOperation",
    "AuthStartSignInParameters",
    "BaseAuthTiming",
)

import typing as t

from ingots.defaults.operations import OperationsOwner, Permissions, PermissionsSlot
from ingots.puer import Factory, Slot, Unit

from .items import (
    AuthAnswerSignInParameters,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInResult,
    AuthStartSignInParameters,
)
from .operations import AuthAnswerSignInOperation, AuthStartSignInOperation
from .permissions import AuthSignInPermissions
from .timings import AuthFloorTiming, AuthNoTiming, BaseAuthTiming


class AuthSignInUnit(OperationsOwner, Unit):
    """
    The operations of the sign-in, a start and the answers to it, and the
    strategy of their timing in the slot ``timing``, none by default.
    """

    permissions = PermissionsSlot(AuthSignInPermissions)

    op_start = Factory(AuthStartSignInOperation)
    op_answer = Factory(AuthAnswerSignInOperation)

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    timing = Slot(BaseAuthTiming)  # type: ignore[type-abstract]

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """What the sign-in gives the anonymous caller: its ``CAN_SIGN_IN``."""
        # always for now: what limits the sign-ins, their number, their rate,
        # comes later as a strategy in a slot, not as a toggle
        return self.permissions(self.permissions.flags.CAN_SIGN_IN)
