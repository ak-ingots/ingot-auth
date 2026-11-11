"""What the storage of the access keeps: a user bound to a group."""

__all__ = ("AuthMembership",)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthMembership:
    """
    The binding of a user to a group, by their uid and name: never the user
    itself, many to many.
    """

    group: str
    uid: str
