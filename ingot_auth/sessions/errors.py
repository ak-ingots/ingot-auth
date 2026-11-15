"""
The errors of the sessions: none tells the token. Those of their storage,
:class:`AuthSessionError` the base of all, are in :mod:`ingot_auth.storages`.
"""

__all__ = ("AuthOwnSessionNotFoundError", "AuthSessionExpiredError")

import typing as t

from ingot_auth.storages import AuthSessionCloseReason, AuthSessionError


class AuthSessionExpiredError(AuthSessionError):
    """The session of the token expired: it is closed for the reason."""

    @classmethod
    def for_reason(cls, reason: AuthSessionCloseReason) -> t.Self:
        return cls(f"the session expired: {reason}", reason)

    @property
    def reason(self) -> AuthSessionCloseReason:
        return t.cast(AuthSessionCloseReason, self.args[1])


class AuthOwnSessionNotFoundError(Exception):
    """
    No open session of the caller has the id: never one, closed, or of
    another. The caller stays signed in; ``args`` are the message, then the
    id.
    """

    @classmethod
    def for_id(cls, session_id: str) -> t.Self:
        return cls(f"no open session {session_id!r} of the caller", session_id)

    @property
    def session_id(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
