"""What the sign-up gives."""

__all__ = (
    "AuthSignUpChallenge",
    "AuthSignedUp",
)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignUpChallenge:
    """The method asks for more: the client answers to the attempt."""

    attempt_uid: str
    challenge: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignedUp:
    """The sign-up is over: the profile is there."""

    uid: str
