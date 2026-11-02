"""The permissions of the attributes of the sessions."""

__all__ = ("AuthSessionAttrsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSessionAttrsPermissions(PermissionFlags, domain="auth.session_attrs"):
    """The operations on the attributes of the sessions."""

    CAN_CREATE = 1 << 0
    CAN_READ = 1 << 1
    CAN_RENAME = 1 << 2
    CAN_DELETE = 1 << 3
