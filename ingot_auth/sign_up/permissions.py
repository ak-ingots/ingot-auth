"""The permissions of the sign-up."""

__all__ = ("AuthSignUpPermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthSignUpPermissions(PermissionFlags, domain="auth.sign_up"):
    """
    The operations of the sign-up: a server gives ``CAN_SIGN_UP`` to who may
    sign up, anyone while the sign-up is open.
    """

    CAN_SIGN_UP = 1 << 0
