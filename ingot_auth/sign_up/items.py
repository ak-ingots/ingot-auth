"""What the sign-up takes, gives and keeps."""

__all__ = (
    "AuthAnswerSignUpParameters",
    "AuthSignUpChallenge",
    "AuthSignUpRecord",
    "AuthSignUpResult",
    "AuthSignedUp",
    "AuthStartSignUpParameters",
)

import datetime
import typing as t
from collections.abc import Mapping
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from ingot_auth.registry import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthStartSignUpParameters:
    """
    A sign-up starting: the method, what the method starts with, and the
    values of the attributes of the session the client gives, by their ids.
    """

    method: str
    parameters: object
    values: "Mapping[int, AuthAttrValue]" = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAnswerSignUpParameters:
    """An answer to the challenge of a sign-up, to its attempt."""

    attempt_id: str
    answer: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignUpChallenge:
    """The method asks for more: the client answers to the attempt."""

    attempt_id: str
    challenge: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignedUp:
    """The sign-up is over: the profile is there."""

    uid: str


AuthSignUpResult: t.TypeAlias = AuthSignUpChallenge | AuthSignedUp


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignUpRecord:
    """
    What a sign-up happened on: the profile, the method, the time and the
    values of the attributes of the session, for the analytics among others.
    Not a session: a sign-up opens none.
    """

    uid: str
    method: str
    signed_up_at: datetime.datetime
    values: "Mapping[int, AuthAttrValue]"
