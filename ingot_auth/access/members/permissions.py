"""The permissions of the members of the groups."""

__all__ = ("AuthMembersPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthMembersPermissions(PermissionFlags, domain="auth.access.members"):
    """The operations on the memberships of the users."""

    CAN_ADD = 1 << 0
    CAN_REMOVE = 1 << 1
    CAN_READ = 1 << 2
