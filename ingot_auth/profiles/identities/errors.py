"""The errors of the identities."""

__all__ = (
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
)

import typing as t


class AuthIdentityError(Exception):
    """
    An error of an identity. ``args`` are the message and the kind, not the
    identifier, an email or a phone that has no place in the logs.
    """

    @property
    def kind(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthIdentityConflictError(AuthIdentityError):
    """The identifier is bound already."""

    @classmethod
    def for_kind(cls, kind: str) -> t.Self:
        return cls(f"{kind}: the identifier is bound already", kind)


class AuthIdentityNotFoundError(AuthIdentityError):
    """The identifier is bound to no profile."""

    @classmethod
    def for_kind(cls, kind: str) -> t.Self:
        return cls(f"{kind}: the identifier is not bound", kind)
