"""The steps of a method: what each call of it ends with."""

__all__ = ("AuthChallenge", "AuthStep", "AuthVerified")

import typing as t
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthChallenge[ChallengeType, StateType]:
    """
    The method asks for more: ``challenge`` goes to the client, ``state`` stays
    with the server until the answer, and never leaves it.
    """

    challenge: ChallengeType
    state: StateType


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthVerified:
    """
    The method has verified who it is: ``subject`` is the one of the method,
    an id of the provider, an email, unique within the method. On a sign-up,
    ``secret`` is what the method keeps to verify the subject on a sign-in,
    the hash of a password, say: the profile is created with it.
    """

    subject: str
    secret: str | None = None


AuthStep: t.TypeAlias = AuthChallenge[t.Any, t.Any] | AuthVerified
