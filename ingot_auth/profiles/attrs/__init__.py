"""The attributes: typed values of the profiles, declared in a registry."""

__all__ = ("AuthAttrsUnit",)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Unit

from .operations import (
    AuthCreateAttrOperation,
    AuthDeleteAttrOperation,
    AuthListAttrsOperation,
    AuthRenameAttrOperation,
)


class AuthAttrsUnit(OperationsOwner, Unit):
    """
    The registry of the attributes: its operations, ``op_*``, which the
    commands of ``cli.auth.profiles.attrs`` run; the attributes themselves
    are in the storage of the auth.
    """

    class Flags(PermissionFlags):
        """The operations on the attributes."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_UPDATE = 1 << 2
        CAN_DELETE = 1 << 3

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateAttrOperation)
    op_list = Factory(AuthListAttrsOperation)
    op_rename = Factory(AuthRenameAttrOperation)
    op_delete = Factory(AuthDeleteAttrOperation)
