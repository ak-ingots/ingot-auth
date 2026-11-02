"""
The contexts of the policies: a policy takes a part of a context, told by a
protocol, and a preset the context made of the parts its policies take.
"""

__all__ = ("AuthHasValue", "AuthValueContext")

import typing as t
from dataclasses import dataclass


class AuthHasValue(t.Protocol):
    """A context with a value, as a user typed it, normalized."""

    async def get_value(self) -> str: ...


@dataclass(frozen=True, slots=True)
class AuthValueContext:
    """The context of a value alone: a nickname, a password signing up."""

    value: str

    async def get_value(self) -> str:
        return self.value
