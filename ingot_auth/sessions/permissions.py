"""The permissions of the sessions: of the caller's own, of a profile."""

__all__ = ("AuthSessionsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSessionsPermissions(PermissionFlags):
    """
    The flags of the domain of the sessions, the full name of their unit,
    ``auth.sessions``: each kept for good, as the masks are stored and sent.
    ``auth.grp_signed_in`` grants a signed-in user its own,
    ``auth.sessions.grp_admins`` the listing of those of a profile, the
    record of its sign-ins.
    """

    CAN_LIST_OWN = 1 << 0
    CAN_REVOKE_OWN = 1 << 1
    CAN_LIST = 1 << 2
