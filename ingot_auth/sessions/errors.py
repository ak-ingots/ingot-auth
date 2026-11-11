"""
The errors of the sessions: none tells the token. Those of their storage,
:class:`AuthSessionError` the base of all, are in :mod:`ingot_auth.storages`.
"""

__all__ = ("AuthSessionExpiredError",)

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
