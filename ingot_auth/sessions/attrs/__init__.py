"""
The attributes of the sessions: typed values of what a sign-up, a sign-in
happened on, the device, the IP, declared in a registry with their sources.
"""

__all__ = (
    "AuthSessionAttrsUnit",
    "build_attr_values",
    "check_client_attr_values",
)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Unit

from .operations import (
    AuthCreateSessionAttrOperation,
    AuthDeleteSessionAttrOperation,
    AuthListSessionAttrsOperation,
    AuthRenameSessionAttrOperation,
)
from .values import build_attr_values, check_client_attr_values


class AuthSessionAttrsUnit(OperationsOwner, Unit):
    """
    The registry of the attributes of the sessions: its operations, ``op_*``,
    which the commands of ``cli.auth.sessions.attrs`` run; the attributes
    themselves are in the storage of the auth.
    """

    class Flags(PermissionFlags):
        """The operations on the attributes of the sessions."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_RENAME = 1 << 2
        CAN_DELETE = 1 << 3

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateSessionAttrOperation)
    op_list = Factory(AuthListSessionAttrsOperation)
    op_rename = Factory(AuthRenameSessionAttrOperation)
    op_delete = Factory(AuthDeleteSessionAttrOperation)
