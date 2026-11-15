"""
The presets of the sessions: what a sign-up, a sign-in asks for of the
attributes of the sessions. A preset is an item of a registry, its bindings
link it to the attributes, many to many, each telling whether the preset
requires the attribute.
"""

__all__ = ("AuthSessionPresetsUnit",)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthBindSessionAttrCommand,
    AuthCreateSessionPresetCommand,
    AuthDeleteSessionPresetCommand,
    AuthListSessionPresetBindingsCommand,
    AuthListSessionPresetsCommand,
    AuthRenameSessionPresetCommand,
    AuthUnbindSessionAttrCommand,
)
from .operations import (
    AuthBindSessionAttrOperation,
    AuthCreateSessionPresetOperation,
    AuthDeleteSessionPresetOperation,
    AuthListSessionPresetBindingsOperation,
    AuthListSessionPresetsOperation,
    AuthRenameSessionPresetOperation,
    AuthUnbindSessionAttrOperation,
)


class AuthSessionPresetsUnit(OperationsOwner, CliUnit):
    """
    The registry of the presets of the sessions with their bindings: its
    operations, ``op_*``, and the commands running them, ``cmd_*``; the
    presets themselves are in the storage of the auth.
    """

    class Flags(PermissionFlags):
        """The operations on the presets of the sessions and their bindings."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_RENAME = 1 << 2
        CAN_DELETE = 1 << 3
        CAN_BIND = 1 << 4
        CAN_UNBIND = 1 << 5

    cli_name = "presets"
    cli_description = "The presets of the sessions."

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateSessionPresetOperation)
    op_list = Factory(AuthListSessionPresetsOperation)
    op_rename = Factory(AuthRenameSessionPresetOperation)
    op_delete = Factory(AuthDeleteSessionPresetOperation)
    op_bind = Factory(AuthBindSessionAttrOperation)
    op_unbind = Factory(AuthUnbindSessionAttrOperation)
    op_list_bindings = Factory(AuthListSessionPresetBindingsOperation)

    cmd_create = Slot(AuthCreateSessionPresetCommand)
    cmd_list = Slot(AuthListSessionPresetsCommand)
    cmd_rename = Slot(AuthRenameSessionPresetCommand)
    cmd_delete = Slot(AuthDeleteSessionPresetCommand)
    cmd_bind = Slot(AuthBindSessionAttrCommand)
    cmd_unbind = Slot(AuthUnbindSessionAttrCommand)
    cmd_list_bindings = Slot(AuthListSessionPresetBindingsCommand)
