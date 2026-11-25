"""The errors of the password."""

__all__ = ("AuthPasswordRefusedError",)

import typing as t

from ingots.puer import UserError


class AuthPasswordRefusedError(UserError):
    """
    A change of the password refused: the old password given is not that of
    the profile, the profile has none, or it was changed meanwhile. Not a
    session gone: the caller stays signed in. ``args`` are the message.
    """

    @classmethod
    def create(cls) -> t.Self:
        return cls("the old password is refused")
