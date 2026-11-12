"""
The parameters of the policies: a policy takes a part of the parameters of
its group, told by a protocol, and a group the parameters made of the parts
its policies take.
"""

__all__ = ("AuthHasValue",)

import typing as t


class AuthHasValue(t.Protocol):
    """Parameters with a value, as a user typed it, normalized."""

    @property
    def value(self) -> str: ...
