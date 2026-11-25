"""The storage of the access."""

__all__ = ("AuthAccessStorage", "AuthMembership", "BaseAuthMembersStorage")

from ingots.puer import Slot, Unit

from .data import AuthMembership
from .members import BaseAuthMembersStorage


class AuthAccessStorage(Unit):
    """
    The storage of the access: the memberships, abstract, all it keeps; the
    groups are of the code.
    """

    members = Slot(BaseAuthMembersStorage)  # type: ignore[type-abstract]
