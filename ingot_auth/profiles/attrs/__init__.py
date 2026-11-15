"""The attributes: typed values of the profiles, declared in a registry."""

__all__ = ("AuthAttrsUnit",)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateAttrCommand,
    AuthDeleteAttrCommand,
    AuthListAttrsCommand,
    AuthRenameAttrCommand,
)
from .operations import (
    AuthCreateAttrOperation,
    AuthDeleteAttrOperation,
    AuthListAttrsOperation,
    AuthRenameAttrOperation,
)
from .values import AuthProfileAttrValuesUnit


class AuthAttrsUnit(OperationsOwner, CliUnit):
    """
    The registry of the attributes: its operations, ``op_*``, and the
    commands running them, ``cmd_*``; the attributes themselves are in the
    storage of the auth.
    """

    class Flags(PermissionFlags):
        """The operations on the attributes."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_UPDATE = 1 << 2
        CAN_DELETE = 1 << 3

    cli_name = "attrs"
    cli_description = "The attributes of the profiles."

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateAttrOperation)
    op_list = Factory(AuthListAttrsOperation)
    op_rename = Factory(AuthRenameAttrOperation)
    op_delete = Factory(AuthDeleteAttrOperation)

    cmd_create = Slot(AuthCreateAttrCommand)
    cmd_list = Slot(AuthListAttrsCommand)
    cmd_rename = Slot(AuthRenameAttrCommand)
    cmd_delete = Slot(AuthDeleteAttrCommand)

    values = Slot(AuthProfileAttrValuesUnit)
