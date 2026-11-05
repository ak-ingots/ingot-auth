"""The errors of the profiles."""

__all__ = (
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
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
