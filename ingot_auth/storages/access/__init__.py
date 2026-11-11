"""The storage of the access."""

__all__ = ("AuthAccessStorage", "AuthMembership", "BaseAuthMembersStorage")

from ingots.puer import Slot, Unit

from .items import AuthMembership
from .members import BaseAuthMembersStorage


class AuthAccessStorage(Unit):
    """
    The storage of the access: the memberships, abstract, all it keeps; the
    groups are of the code.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    members = Slot(BaseAuthMembersStorage)  # type: ignore[type-abstract]
