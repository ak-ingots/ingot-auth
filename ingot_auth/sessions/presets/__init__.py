"""
The presets of the sessions: what a sign-up, a sign-in asks for of the
attributes of the sessions. A preset is an item of a registry, its bindings
link it to the attributes, many to many, each telling whether the preset
requires the attribute.
"""

__all__ = (
    "AuthSessionPreset",
    "AuthSessionPresetBinding",
    "AuthSessionPresets",
    "AuthSessionPresetsPermissions",
    "BaseAuthSessionPresetsStorage",
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
from .items import AuthSessionPreset, AuthSessionPresetBinding
from .operations import (
    AuthBindSessionAttr,
    AuthCreateSessionPreset,
    AuthDeleteSessionPreset,
    AuthListSessionPresetBindings,
    AuthListSessionPresets,
    AuthRenameSessionPreset,
    AuthUnbindSessionAttr,
)
from .permissions import AuthSessionPresetsPermissions
from .storage import BaseAuthSessionPresetsStorage


class AuthSessionPresets(CliUnit):
    """
    The registry of the presets of the sessions with their bindings: its
    operations, ``op_*``, and the commands running them, ``cmd_*``; the
    presets themselves are in the storage of the auth.
    """

    cli_name = "presets"
    cli_description = "The presets of the sessions."

    op_create = Factory(AuthCreateSessionPreset)
    op_list = Factory(AuthListSessionPresets)
    op_rename = Factory(AuthRenameSessionPreset)
    op_delete = Factory(AuthDeleteSessionPreset)
    op_bind = Factory(AuthBindSessionAttr)
    op_unbind = Factory(AuthUnbindSessionAttr)
    op_list_bindings = Factory(AuthListSessionPresetBindings)

    cmd_create = Slot(AuthCreateSessionPresetCommand)
    cmd_list = Slot(AuthListSessionPresetsCommand)
    cmd_rename = Slot(AuthRenameSessionPresetCommand)
    cmd_delete = Slot(AuthDeleteSessionPresetCommand)
    cmd_bind = Slot(AuthBindSessionAttrCommand)
    cmd_unbind = Slot(AuthUnbindSessionAttrCommand)
    cmd_list_bindings = Slot(AuthListSessionPresetBindingsCommand)
