"""The permissions of the tags."""

__all__ = ("AuthTagsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthTagsPermissions(PermissionFlags, domain="auth.tags"):
    """The operations on the tags."""

    CAN_CREATE = 1 << 0
    CAN_READ = 1 << 1
    CAN_UPDATE = 1 << 2
    CAN_DELETE = 1 << 3
