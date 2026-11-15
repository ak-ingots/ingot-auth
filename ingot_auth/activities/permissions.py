"""The permissions of the activity log."""

__all__ = ("AuthActivitiesPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthActivitiesPermissions(PermissionFlags):
    """
    The flags of the domain of the log, the full name of its unit,
    ``auth.activities``: each kept for good. ``auth.activities.grp_auditors``
    grants the reading of it.
    """

    CAN_READ = 1 << 0
