"""The errors of the storage of the sessions: none tells the token."""

__all__ = ("AuthSessionError", "AuthSessionNotFoundError")

import typing as t

from ingots.puer import UserError


class AuthSessionError(UserError):
    """
    An error of a session: a client signs in again. ``args`` are the message,
    then what it is of.
    """

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthSessionNotFoundError(AuthSessionError):
    """No open session has the token, or the uid: never one, or closed."""

    @classmethod
    def for_token(cls) -> t.Self:
        return cls("no open session has the token")

    @classmethod
    def for_uid(cls, session_uid: str) -> t.Self:
        return cls(f"no open session {session_uid!r}", session_uid)
