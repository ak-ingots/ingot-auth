"""The permissions of the metadata."""

__all__ = ("AuthMetadataPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthMetadataPermissions(PermissionFlags, domain="auth.metadata"):
    """The operations on the metadata."""

    CAN_READ = 1 << 0
