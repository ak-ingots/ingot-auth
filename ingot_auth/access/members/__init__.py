"""The members of the groups: the memberships, the users bound to them."""

__all__ = (
    "AuthAddMemberOperation",
    "AuthAddMemberCommand",
    "AuthListMemberGroupsOperation",
    "AuthListMemberGroupsCommand",
    "AuthListMembersOperation",
    "AuthListMembersCommand",
    "AuthMembersUnit",
    "AuthRemoveMemberOperation",
    "AuthRemoveMemberCommand",
)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthAddMemberCommand,
    AuthListMemberGroupsCommand,
    AuthListMembersCommand,
    AuthRemoveMemberCommand,
)

from .operations import (
    AuthAddMemberOperation,
    AuthListMemberGroupsOperation,
    AuthListMembersOperation,
    AuthRemoveMemberOperation,
)


class AuthMembersUnit(OperationsOwner, CliUnit):
    """
    The operations of the memberships, ``op_*``, and the commands running
    them, ``cmd_*``; the memberships themselves are in the storage of the
    auth.
    """

    class Flags(PermissionFlags):
        """The operations on the memberships of the users."""

        CAN_ADD = 1 << 0
        CAN_REMOVE = 1 << 1
        CAN_READ = 1 << 2

    cli_name = "members"
    cli_description = "The members of the groups."

    permissions = PermissionsSlot(Flags)

    op_add = Factory(AuthAddMemberOperation)
    op_remove = Factory(AuthRemoveMemberOperation)
    op_list = Factory(AuthListMembersOperation)
    op_list_groups = Factory(AuthListMemberGroupsOperation)

    cmd_add = Slot(AuthAddMemberCommand)
    cmd_remove = Slot(AuthRemoveMemberCommand)
    cmd_list = Slot(AuthListMembersCommand)
    cmd_list_groups = Slot(AuthListMemberGroupsCommand)
