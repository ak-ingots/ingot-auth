"""The permissions of the presets of the sessions."""

__all__ = ("AuthSessionPresetsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSessionPresetsPermissions(PermissionFlags):
    """The operations on the presets of the sessions and their bindings."""

    CAN_CREATE = 1 << 0
    CAN_READ = 1 << 1
    CAN_RENAME = 1 << 2
    CAN_DELETE = 1 << 3
    CAN_BIND = 1 << 4
    CAN_UNBIND = 1 << 5
