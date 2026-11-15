"""The tags: marks on the profiles, declared in a registry."""

__all__ = ("AuthTagsUnit",)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateTagCommand,
    AuthDeleteTagCommand,
    AuthListTagsCommand,
    AuthRenameTagCommand,
    AuthSetProfileTagsCommand,
)
from .operations import (
    AuthCreateTagOperation,
    AuthDeleteTagOperation,
    AuthListTagsOperation,
    AuthRenameTagOperation,
)


class AuthTagsUnit(OperationsOwner, CliUnit):
    """
    The registry of the tags: its operations, ``op_*``, and the commands
    running them, ``cmd_*``; the tags themselves are in the storage of the
    auth.
    """

    class Flags(PermissionFlags):
        """The operations on the tags."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_UPDATE = 1 << 2
        CAN_DELETE = 1 << 3

    cli_name = "tags"
    cli_description = "The tags of the profiles."

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateTagOperation)
    op_list = Factory(AuthListTagsOperation)
    op_rename = Factory(AuthRenameTagOperation)
    op_delete = Factory(AuthDeleteTagOperation)

    cmd_create = Slot(AuthCreateTagCommand)
    cmd_list = Slot(AuthListTagsCommand)
    cmd_rename = Slot(AuthRenameTagCommand)
    cmd_delete = Slot(AuthDeleteTagCommand)
    cmd_set = Slot(AuthSetProfileTagsCommand)
