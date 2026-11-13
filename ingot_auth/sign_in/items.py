"""What the sign-in takes and gives."""

__all__ = (
    "AuthAnswerSignInParameters",
    "AuthSignInChallenge",
    "AuthSignInResult",
    "AuthSignedIn",
    "AuthStartSignInParameters",
)

import typing as t
from collections.abc import Mapping
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthStartSignInParameters:
    """
    A sign-in starting: the method, what the method starts with, and the
    values of the attributes of the session, kept by the session: those the
    client gives, by their ids, and those the transport gives, by their
    names, which the transport alone sets, never from what the client sends.
    """

    method: str
    parameters: object
    attr_values: "Mapping[int, AuthAttrValue]" = field(default_factory=dict)
    transport_attr_values: "Mapping[str, AuthAttrValue]" = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAnswerSignInParameters:
    """An answer to the challenge of a sign-in, to its attempt."""

    attempt_id: str
    answer: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignInChallenge:
    """The method asks for more: the client answers to the attempt."""

    attempt_id: str
    challenge: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignedIn:
    """
    The sign-in is over: a session is open, its token given once, never in a
    ``repr``, the client sending it with each call, and its id, public.
    """

    session_id: str
    token: str = field(repr=False)


AuthSignInResult: t.TypeAlias = AuthSignInChallenge | AuthSignedIn
