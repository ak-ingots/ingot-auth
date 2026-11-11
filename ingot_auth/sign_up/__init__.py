"""
The sign-up: a method verifies who it is, in steps, and the sign-up creates
the profile, binds the subject of the method to it and keeps the record of
what it happened on. It opens no session.
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


class AuthSignUpUnit(Unit):
    """The operations of the sign-up: a start and the answers to it."""

    op_start = Factory(AuthStartSignUpOperation)
    op_answer = Factory(AuthAnswerSignUpOperation)
