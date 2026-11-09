"""The permissions of the groups."""

__all__ = ("AuthGroupsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthGroupsPermissions(PermissionFlags, domain="auth.access.groups"):
    """The operations on the groups, which the code declares: reading them."""

    CAN_READ = 1 << 0
