"""The members of the groups: the memberships, the users bound to them."""

__all__ = (
    "AuthAddMember",
    "AuthAddMemberCommand",
    "AuthListMemberGroups",
    "AuthListMemberGroupsCommand",
    "AuthListMembers",
    "AuthListMembersCommand",
    "AuthMembers",
    "AuthMembersPermissions",
    "AuthMembership",
    "AuthRemoveMember",
    "AuthRemoveMemberCommand",
    "BaseAuthMembersStorage",
)

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthAddMemberCommand,
    AuthListMemberGroupsCommand,
    AuthListMembersCommand,
    AuthRemoveMemberCommand,
)

from .items import AuthMembership
from .operations import (
    AuthAddMember,
    AuthListMemberGroups,
    AuthListMembers,
    AuthRemoveMember,
)
from .permissions import AuthMembersPermissions
from .storage import BaseAuthMembersStorage


class AuthMembers(CliUnit):
    """
    The operations of the memberships, ``op_*``, and the commands running
    them, ``cmd_*``; the memberships themselves are in the storage of the
    auth.
    """

    cli_name = "members"
    cli_description = "The members of the groups."

    op_add = Factory(AuthAddMember)
    op_remove = Factory(AuthRemoveMember)
    op_list = Factory(AuthListMembers)
    op_list_groups = Factory(AuthListMemberGroups)

    cmd_add = Slot(AuthAddMemberCommand)
    cmd_remove = Slot(AuthRemoveMemberCommand)
    cmd_list = Slot(AuthListMembersCommand)
    cmd_list_groups = Slot(AuthListMemberGroupsCommand)
