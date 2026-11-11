"""The permissions of the sign-in."""

__all__ = ("AuthSignInPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSignInPermissions(PermissionFlags, domain="auth.sign_in"):
    """
    The operations of the sign-in: a server gives ``CAN_SIGN_IN`` to who may
    sign in, anyone while the sign-in is open.
    """

    CAN_SIGN_IN = 1 << 0
