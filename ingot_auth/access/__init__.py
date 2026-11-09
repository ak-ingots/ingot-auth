"""
The access: the groups of the users, what each grants, and the members of
each. The permissions of a signed-in user are the union of what its groups
grant, by the strategy of the slot ``permissions``. An application declares
its groups in its own :class:`AuthGroups`::

    class AppAccess(AuthAccess):
        groups = Slot(AppGroups)
"""

__all__ = ("AuthAccess", "AuthAccessStorage", "AuthGroupsGrants")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .groups import AuthGroups
from .members import AuthMembers
from .storage import AuthAccessStorage
from .strategies import AuthGroupsGrants


class AuthAccess(CliUnit):
    """The access: the groups, their members and the permissions of a user."""

    cli_name = "access"
    cli_description = "The groups of the users and their members."

    groups = Slot(AuthGroups)
    members = Slot(AuthMembers)
    permissions = Slot(AuthGroupsGrants)
