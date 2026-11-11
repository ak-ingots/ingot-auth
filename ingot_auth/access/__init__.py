"""
The access: the groups of the users, what each grants, and the members of
each. The permissions of a signed-in user are the union of what its groups
grant, by the strategy of the slot ``permissions``. An application declares
its groups in its own :class:`AuthGroupsUnit`::

    class AppAccessUnit(AuthAccessUnit):
        groups = Slot(AppGroupsUnit)
"""

__all__ = ("AuthAccessUnit", "AuthGroupsGrants")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .groups import AuthGroupsUnit
from .members import AuthMembersUnit
from .strategies import AuthGroupsGrants


class AuthAccessUnit(CliUnit):
    """The access: the groups, their members and the permissions of a user."""

    cli_name = "access"
    cli_description = "The groups of the users and their members."

    groups = Slot(AuthGroupsUnit)
    members = Slot(AuthMembersUnit)
    permissions = Slot(AuthGroupsGrants)
