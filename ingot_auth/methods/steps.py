"""The steps of a method: what each call of it ends with."""

__all__ = ("AuthChallenge", "AuthCodeChallenge", "AuthStep", "AuthVerified")

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
class AuthCodeChallenge:
    """
    What a step asks for, by any method or factor: a code of ``length`` digits
    sent to the user, by mail, an SMS, an app, which the client shows the form
    of; the client answers with the code typed.
    """

    length: int


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
