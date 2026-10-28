"""The attributes: typed values of the profiles, declared in a registry."""

__all__ = (
    "AuthAttr",
    "AuthAttrType",
    "AuthAttrs",
    "AuthMemoryAttrsStorage",
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
from .items import AuthAttr, AuthAttrType
from .operations import AuthCreateAttr, AuthDeleteAttr, AuthListAttrs, AuthRenameAttr
from .storage import AuthMemoryAttrsStorage, BaseAuthAttrsStorage


class AuthAttrs(CliUnit):
    """
    The registry of the attributes: its operations, ``op_*``, and the
    commands running them, ``cmd_*``; the attributes themselves are in the
    storage of the auth.
    """

    cli_name = "attrs"
    cli_description = "The attributes of the profiles."

    op_create = Factory(AuthCreateAttr)
    op_list = Factory(AuthListAttrs)
    op_rename = Factory(AuthRenameAttr)
    op_delete = Factory(AuthDeleteAttr)

    cmd_create = Slot(AuthCreateAttrCommand)
    cmd_list = Slot(AuthListAttrsCommand)
    cmd_rename = Slot(AuthRenameAttrCommand)
    cmd_delete = Slot(AuthDeleteAttrCommand)
