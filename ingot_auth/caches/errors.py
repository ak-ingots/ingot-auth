"""The errors of the caches."""

__all__ = ("AuthAttemptNotFoundError",)

import typing as t


class AuthAttemptNotFoundError(Exception):
    """
    No attempt has the id: there never was one, it expired or it is over.
    ``args`` are the message.
    """

    @classmethod
    def create(cls) -> t.Self:
        return cls("no such attempt")

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
