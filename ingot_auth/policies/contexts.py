"""
The contexts of the policies: a policy takes a part of a context, told by a
protocol, and a preset the context made of the parts its policies take.
"""

__all__ = ("AuthHasValue", "AuthValueContext")

import typing as t


class AuthHasValue(t.Protocol):
    """A context with a value, as a user typed it, normalized."""

    async def get_value(self) -> str: ...


class AuthValueContext:
    """
    The context of a value alone: a nickname, a password signing up. A
    context gives its parts by the methods of its protocols only, its data
    private: none of it in its ``repr``.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    async def get_value(self) -> str:
        return self._value
