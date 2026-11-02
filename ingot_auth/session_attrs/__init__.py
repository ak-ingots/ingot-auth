"""
The attributes of the sessions: typed values of what a sign-up, a sign-in
happened on, the device, the IP, declared in a registry with their sources.
"""

__all__ = (
    "AuthSessionAttr",
    "AuthSessionAttrSource",
    "AuthSessionAttrs",
    "AuthSessionAttrsPermissions",
    "BaseAuthSessionAttrsStorage",
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
    AuthCreateSessionAttr,
    AuthDeleteSessionAttr,
    AuthListSessionAttrs,
    AuthRenameSessionAttr,
)
from .permissions import AuthSessionAttrsPermissions
from .storage import BaseAuthSessionAttrsStorage


class AuthSessionAttrs(CliUnit):
    """
    The registry of the attributes of the sessions: its operations, ``op_*``,
    and the commands running them, ``cmd_*``; the attributes themselves are in
    the storage of the auth.
    """

    cli_name = "session-attrs"
    cli_description = "The attributes of the sessions."

    op_create = Factory(AuthCreateSessionAttr)
    op_list = Factory(AuthListSessionAttrs)
    op_rename = Factory(AuthRenameSessionAttr)
    op_delete = Factory(AuthDeleteSessionAttr)

    cmd_create = Slot(AuthCreateSessionAttrCommand)
    cmd_list = Slot(AuthListSessionAttrsCommand)
    cmd_rename = Slot(AuthRenameSessionAttrCommand)
    cmd_delete = Slot(AuthDeleteSessionAttrCommand)
