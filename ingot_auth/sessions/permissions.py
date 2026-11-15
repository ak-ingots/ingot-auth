"""The permissions of the sessions of the caller's own."""

__all__ = ("AuthSessionsPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSessionsPermissions(PermissionFlags):
    """
    The flags of the domain of the sessions, the full name of their unit,
    ``auth.sessions``: each kept for good, as the masks are stored and sent.
    ``auth.grp_signed_in`` grants a signed-in user its own.
    """

    CAN_LIST_OWN = 1 << 0
    CAN_REVOKE_OWN = 1 << 1
