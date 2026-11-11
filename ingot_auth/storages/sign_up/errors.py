"""The errors of the sign-up."""

__all__ = ("AuthSignUpRecordNotFoundError",)

import typing as t


class AuthSignUpRecordNotFoundError(Exception):
    """No record has the uid. ``args`` are the message and the uid."""

    @classmethod
    def for_uid(cls, uid: str) -> t.Self:
        return cls(f"no sign-up of {uid!r}", uid)

    @property
    def uid(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
