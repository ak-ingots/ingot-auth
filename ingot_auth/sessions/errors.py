"""The errors of the sessions: none tells the token."""

__all__ = (
    "AuthSessionError",
    "AuthSessionExpiredError",
    "AuthSessionNotFoundError",
)

import typing as t

from .items import AuthSessionCloseReason


class AuthSessionError(Exception):
    """
    An error of a session: a client signs in again. ``args`` are the message,
    then what it is of.
    """

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthSessionNotFoundError(AuthSessionError):
    """No open session has the token, or the id: never one, or closed."""

    @classmethod
    def for_token(cls) -> t.Self:
        return cls("no open session has the token")

    @classmethod
    def for_id(cls, session_id: str) -> t.Self:
        return cls(f"no open session {session_id!r}", session_id)


class AuthSessionExpiredError(AuthSessionError):
    """The session of the token expired: it is closed for the reason."""

    @classmethod
    def for_reason(cls, reason: AuthSessionCloseReason) -> t.Self:
        return cls(f"the session expired: {reason}", reason)

    @property
    def reason(self) -> AuthSessionCloseReason:
        return t.cast(AuthSessionCloseReason, self.args[1])
