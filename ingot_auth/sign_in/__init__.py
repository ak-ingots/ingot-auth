"""
The sign-in: a method verifies who it is, in steps, and the sign-in finds the
profile bound to what the method verified, checks the profile may sign in by
the method and opens a session of it, giving its token.
"""

__all__ = (
    "AuthAnswerSignInOperation",
    "AuthAnswerSignInParameters",
    "AuthSignInChallenge",
    "AuthSignInPermissions",
    "AuthSignInResult",
    "AuthSignInUnit",
    "AuthSignedIn",
    "AuthStartSignInOperation",
    "AuthStartSignInParameters",
)

from ingots.puer import Factory, Unit

from .items import (
    AuthAnswerSignInParameters,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInResult,
    AuthStartSignInParameters,
)
from .operations import AuthAnswerSignInOperation, AuthStartSignInOperation
from .permissions import AuthSignInPermissions


class AuthSignInUnit(Unit):
    """The operations of the sign-in: a start and the answers to it."""

    op_start = Factory(AuthStartSignInOperation)
    op_answer = Factory(AuthAnswerSignInOperation)
