"""The errors of the sign-up."""

__all__ = ("AuthSignUpRecordNotFoundError",)

import typing as t

from ingots.puer import UserError


class AuthSignUpRecordNotFoundError(UserError):
    """No record has the uid. ``args`` are the message and the uid."""

    args: tuple[str, str]

    @classmethod
    def for_uid(cls, uid: str) -> t.Self:
        return cls(f"no sign-up of {uid!r}", uid)

    @property
    def uid(self) -> str:
        return self.args[1]

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
