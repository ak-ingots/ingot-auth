"""What the sign-up takes and gives."""

__all__ = (
    "AuthAnswerSignUpParameters",
    "AuthSignUpChallenge",
    "AuthSignUpResult",
    "AuthSignedUp",
    "AuthStartSignUpParameters",
)

import typing as t
from collections.abc import Mapping
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthStartSignUpParameters:
    """
    A sign-up starting: the method, what the method starts with, and the
    values of the attributes of the session, kept by the record of the
    sign-up: those the client gives, by their ids, and those the transport
    gives, by their names, which the transport alone sets, never from what
    the client sends.
    """

    method: str
    parameters: object
    attr_values: "Mapping[int, AuthAttrValue]" = field(default_factory=dict)
    transport_attr_values: "Mapping[str, AuthAttrValue]" = field(default_factory=dict)


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
