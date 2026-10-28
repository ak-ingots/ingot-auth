"""The permissions of the auth."""

__all__ = ("AuthPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthPermissions(PermissionFlags, domain="auth"):
    """The permissions of the domain ``auth``."""

    READ_REGISTRY = 1 << 0  # reads the registries: the tags, the attributes
    MANAGE_REGISTRY = 1 << 1  # creates, renames, deletes their items
