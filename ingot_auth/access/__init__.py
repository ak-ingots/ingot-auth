"""
The access: the groups of the users, what each grants, and the members of
each. The permissions of a signed-in user are the union of what its groups
grant, by the strategy of the slot ``permissions``. The groups are in the
units of their domains, :class:`~.groups.AuthGroupsOwner`, found by
:class:`AuthGroupsUnit`.
"""

__all__ = ("AuthAccessUnit", "AuthGroupsGrants")

from ingots.puer import Slot, Unit

from .groups import AuthGroupsUnit
from .members import AuthMembersUnit
from .strategies import AuthGroupsGrants


class AuthAccessUnit(Unit):
    """The access: the groups, their members and the permissions of a user."""

    groups = Slot(AuthGroupsUnit)
    members = Slot(AuthMembersUnit)
    permissions = Slot(AuthGroupsGrants)
