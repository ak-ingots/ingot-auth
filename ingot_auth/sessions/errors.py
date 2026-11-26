"""
The errors of the sessions: none tells the token. Those of their storage,
:class:`AuthSessionError` the base of all, are in :mod:`ingot_auth.storages`.
"""

__all__ = (
    "AuthOwnSessionNotFoundError",
    "AuthSessionExpiredError",
    "AuthSessionsLimitError",
)

import typing as t

from ingots.puer import UserError

from ingot_auth.storages import AuthSessionCloseReason, AuthSessionError


class AuthSessionExpiredError(AuthSessionError):
    """The session of the token expired: it is closed for the reason."""

    args: tuple[str, AuthSessionCloseReason]

    @classmethod
    def for_reason(cls, reason: AuthSessionCloseReason) -> t.Self:
        return cls(f"the session expired: {reason}", reason)

    @property
    def reason(self) -> AuthSessionCloseReason:
        return self.args[1]


class AuthOwnSessionNotFoundError(UserError):
    """
    No open session of the caller has the uid: never one, closed, or of
    another. The caller stays signed in; ``args`` are the message, then the
    uid.
    """

    args: tuple[str, str]

    @classmethod
    def for_uid(cls, session_uid: str) -> t.Self:
        return cls(f"no open session {session_uid!r} of the caller", session_uid)

    @property
    def session_uid(self) -> str:
        return self.args[1]

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthSessionsLimitError(UserError):
    """
    A sign-in refused: the profile has as many open sessions as
    ``AUTH_SESSIONS_MAX`` allows, the strategy of the limit refusing. The
    user signs out of another first; ``args`` are the message, then how many.
    """

    args: tuple[str, int]

    @classmethod
    def for_count(cls, count: int) -> t.Self:
        return cls(f"as many open sessions as allowed: {count}", count)

    @property
    def count(self) -> int:
        return self.args[1]

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
