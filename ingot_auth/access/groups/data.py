"""What the operations of the groups give."""

__all__ = ("AuthGroupInfo",)

from dataclasses import dataclass

from ingots.defaults.operations import Permissions


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthGroupInfo:
    """A group as an operator reads it: its name and what it grants."""

    name: str
    permissions: Permissions
