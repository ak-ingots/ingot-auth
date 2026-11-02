"""The errors of the transactions of the storage."""

__all__ = ("AuthTransactionError",)

import typing as t


class AuthTransactionError(Exception):
    """
    A transaction is begun, committed or rolled back out of turn: a call of
    the storage is wrong, not the data. ``args`` are the message.
    """

    @classmethod
    def for_begun(cls) -> t.Self:
        return cls("a transaction is begun already")

    @classmethod
    def for_not_begun(cls) -> t.Self:
        return cls("no transaction is begun")

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
