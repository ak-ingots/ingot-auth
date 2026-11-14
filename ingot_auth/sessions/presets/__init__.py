"""
The presets of the sessions: what a sign-up, a sign-in asks for of the
attributes of the sessions. A preset is an item of a registry, its bindings
link it to the attributes, many to many, each telling whether the preset
requires the attribute.
"""

__all__ = (
    "AuthSessionPresetsUnit",
    "AuthSessionPresetsPermissions",
)

from ingots.defaults.operations import OperationsOwner, PermissionsSlot
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
from .permissions import AuthSessionPresetsPermissions


class AuthSessionPresetsUnit(OperationsOwner, CliUnit):
    """
    The registry of the presets of the sessions with their bindings: its
    operations, ``op_*``, and the commands running them, ``cmd_*``; the
    presets themselves are in the storage of the auth.
    """

    cli_name = "presets"
    cli_description = "The presets of the sessions."

    permissions = PermissionsSlot(AuthSessionPresetsPermissions)

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
