"""The permissions of the profiles themselves, their values."""

__all__ = ("AuthProfilesPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthProfilesPermissions(PermissionFlags):
    """
    The flags of the domain of the profiles, the full name of their unit,
    ``auth.profiles``: each kept for good, as the masks are stored and sent.
    ``auth.profiles.grp_managers`` grants the setting of their values.
    """

    CAN_UPDATE = 1 << 0
