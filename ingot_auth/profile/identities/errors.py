"""The errors of the identities."""

__all__ = (
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
)

import typing as t


class AuthIdentityError(Exception):
    """
    An error of an identity. ``args`` are the message and the method, not the
    subject, an email or a phone that has no place in the logs.
    """

    @property
    def method(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthIdentityConflictError(AuthIdentityError):
    """The subject is bound already."""

    @classmethod
    def for_method(cls, method: str) -> t.Self:
        return cls(f"{method}: the subject is bound already", method)


class AuthIdentityNotFoundError(AuthIdentityError):
    """The subject is bound to no profile."""

    @classmethod
    def for_method(cls, method: str) -> t.Self:
        return cls(f"{method}: the subject is not bound", method)
