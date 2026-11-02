"""
The sign-up: a method verifies who it is, in steps, and the sign-up creates
the profile, binds the subject of the method to it and keeps the record of
what it happened on. It opens no session.
"""

__all__ = (
    "AuthAnswerSignUp",
    "AuthAnswerSignUpParameters",
    "AuthSignUpChallenge",
    "AuthSignUpPermissions",
    "AuthSignUpRecord",
    "AuthSignUpRecordNotFoundError",
    "AuthSignUpResult",
    "AuthSignUpStorage",
    "AuthSignUpUnit",
    "AuthSignedUp",
    "AuthStartSignUp",
    "AuthStartSignUpParameters",
    "BaseAuthSignUpRecordsStorage",
)

from ingots.puer import Factory, Unit

from .errors import AuthSignUpRecordNotFoundError
from .items import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpRecord,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from .operations import AuthAnswerSignUp, AuthStartSignUp
from .permissions import AuthSignUpPermissions
from .storage import (
    AuthSignUpStorage,
    BaseAuthSignUpRecordsStorage,
)


class AuthSignUpUnit(Unit):
    """The operations of the sign-up: a start and the answers to it."""

    op_start = Factory(AuthStartSignUp)
    op_answer = Factory(AuthAnswerSignUp)
