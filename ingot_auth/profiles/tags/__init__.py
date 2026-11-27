"""The tags: marks on the profiles, declared in a registry."""

__all__ = ("AuthTagsUnit",)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Unit

from .operations import (
    AuthCreateTagOperation,
    AuthDeleteTagOperation,
    AuthListTagsOperation,
    AuthRenameTagOperation,
)


class AuthTagsUnit(OperationsOwner, Unit):
    """
    The registry of the tags: its operations, ``op_*``, which the commands
    of ``cli.auth.profiles.tags`` run; the tags themselves are in the
    storage of the auth.
    """

    class Flags(PermissionFlags):
        """The operations on the tags."""

        CAN_CREATE = 1 << 0
        CAN_READ = 1 << 1
        CAN_UPDATE = 1 << 2
        CAN_DELETE = 1 << 3

    permissions = PermissionsSlot(Flags)

    op_create = Factory(AuthCreateTagOperation)
    op_list = Factory(AuthListTagsOperation)
    op_rename = Factory(AuthRenameTagOperation)
    op_delete = Factory(AuthDeleteTagOperation)
