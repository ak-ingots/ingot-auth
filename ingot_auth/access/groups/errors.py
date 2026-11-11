"""The errors of the groups."""

__all__ = ("AuthGroupError", "AuthGroupNotFoundError")

import typing as t


class AuthGroupError(Exception):
    """
    An error of a group. ``args`` are the message and the name of the
    group, so the error survives pickling; create it with the class methods
    of its subclasses.
    """

    @property
    def name(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthGroupNotFoundError(AuthGroupError):
    """No group has the name, or the group keeps no members to tell of."""

    @classmethod
    def for_name(cls, name: str) -> t.Self:
        """No source of the groups has one of the name."""
        return cls(f"no group {name!r}", name)

    @classmethod
    def for_members(cls, name: str) -> t.Self:
        """
        The group keeps no members: every signed-in user is one, none is
        added, removed or listed.
        """
        return cls(f"the group {name!r} has every signed-in user", name)
