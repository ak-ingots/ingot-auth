"""The errors of the secrets."""

__all__ = ("AuthSecretNotFoundError",)

import typing as t


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
