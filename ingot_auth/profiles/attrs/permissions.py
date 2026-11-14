"""The permissions of the attributes."""

__all__ = ("AuthAttrsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthAttrsPermissions(PermissionFlags):
    """The operations on the attributes."""

    CAN_CREATE = 1 << 0
    CAN_READ = 1 << 1
    CAN_UPDATE = 1 << 2
    CAN_DELETE = 1 << 3
