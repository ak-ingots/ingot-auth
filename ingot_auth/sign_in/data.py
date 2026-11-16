"""What the sign-in gives."""

__all__ = ("AuthSignInChallenge", "AuthSignedIn")

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignInChallenge:
    """The method asks for more: the client answers to the attempt."""

    attempt_uid: str
    challenge: object


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignedIn:
    """
    The sign-in is over: a session is open, its token given once, never in a
    ``repr``, the client sending it with each call, and its id, public.
    """

    session_uid: str
    token: str = field(repr=False)
