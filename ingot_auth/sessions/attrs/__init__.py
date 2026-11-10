"""
The attributes of the sessions: typed values of what a sign-up, a sign-in
happened on, the device, the IP, declared in a registry with their sources.
"""

__all__ = (
    "AuthSessionAttr",
    "AuthSessionAttrSource",
    "AuthSessionAttrsUnit",
    "AuthSessionAttrsPermissions",
    "BaseAuthSessionAttrsStorage",
    "check_client_values",
)

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateSessionAttrCommand,
    AuthDeleteSessionAttrCommand,
    AuthListSessionAttrsCommand,
    AuthRenameSessionAttrCommand,
)
from .items import AuthSessionAttr, AuthSessionAttrSource
from .operations import (
    AuthCreateSessionAttrOperation,
    AuthDeleteSessionAttrOperation,
    AuthListSessionAttrsOperation,
    AuthRenameSessionAttrOperation,
)
from .permissions import AuthSessionAttrsPermissions
from .storage import BaseAuthSessionAttrsStorage
from .values import check_client_values


class AuthSessionAttrsUnit(CliUnit):
    """
    The registry of the attributes of the sessions: its operations, ``op_*``,
    and the commands running them, ``cmd_*``; the attributes themselves are in
    the storage of the auth.
    """

    cli_name = "attrs"
    cli_description = "The attributes of the sessions."

    op_create = Factory(AuthCreateSessionAttrOperation)
    op_list = Factory(AuthListSessionAttrsOperation)
    op_rename = Factory(AuthRenameSessionAttrOperation)
    op_delete = Factory(AuthDeleteSessionAttrOperation)

    cmd_create = Slot(AuthCreateSessionAttrCommand)
    cmd_list = Slot(AuthListSessionAttrsCommand)
    cmd_rename = Slot(AuthRenameSessionAttrCommand)
    cmd_delete = Slot(AuthDeleteSessionAttrCommand)
