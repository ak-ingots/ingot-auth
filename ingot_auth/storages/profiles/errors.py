"""The errors of the storage of the profiles, their identities and secrets."""

__all__ = (
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
    "AuthSecretNotFoundError",
)

import typing as t


class AuthProfileError(Exception):
    """An error of a profile. ``args`` are the message and the uid."""

    @property
    def uid(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthProfileConflictError(AuthProfileError):
    """The uid is taken."""

    @classmethod
    def for_uid(cls, uid: str) -> t.Self:
        return cls(f"the uid {uid!r} is taken", uid)


class AuthProfileNotFoundError(AuthProfileError):
    """No profile has the uid."""

    @classmethod
    def for_uid(cls, uid: str) -> t.Self:
        return cls(f"no profile {uid!r}", uid)


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


class AuthSecretNotFoundError(Exception):
    """The profile has no secret. ``args`` are the message and the uid."""

    @classmethod
    def for_uid(cls, uid: str) -> t.Self:
        return cls(f"the profile {uid!r} has no secret", uid)

    @property
    def uid(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
