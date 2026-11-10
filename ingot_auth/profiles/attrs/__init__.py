"""The attributes: typed values of the profiles, declared in a registry."""

__all__ = (
    "AuthAttr",
    "AuthAttrsUnit",
    "AuthAttrsPermissions",
    "BaseAuthAttrsStorage",
)

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateAttrCommand,
    AuthDeleteAttrCommand,
    AuthListAttrsCommand,
    AuthRenameAttrCommand,
)
from .items import AuthAttr
from .operations import (
    AuthCreateAttrOperation,
    AuthDeleteAttrOperation,
    AuthListAttrsOperation,
    AuthRenameAttrOperation,
)
from .permissions import AuthAttrsPermissions
from .storage import BaseAuthAttrsStorage


class AuthAttrsUnit(CliUnit):
    """
    The registry of the attributes: its operations, ``op_*``, and the
    commands running them, ``cmd_*``; the attributes themselves are in the
    storage of the auth.
    """

    cli_name = "attrs"
    cli_description = "The attributes of the profiles."

    op_create = Factory(AuthCreateAttrOperation)
    op_list = Factory(AuthListAttrsOperation)
    op_rename = Factory(AuthRenameAttrOperation)
    op_delete = Factory(AuthDeleteAttrOperation)

    cmd_create = Slot(AuthCreateAttrCommand)
    cmd_list = Slot(AuthListAttrsCommand)
    cmd_rename = Slot(AuthRenameAttrCommand)
    cmd_delete = Slot(AuthDeleteAttrCommand)
