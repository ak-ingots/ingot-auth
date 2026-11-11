"""The errors of the storage of the sessions: none tells the token."""

__all__ = ("AuthSessionError", "AuthSessionNotFoundError")

import typing as t


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
