"""The permissions of the method of an email and a code sent to it."""

__all__ = ("AuthEmailCodePermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthEmailCodePermissions(PermissionFlags):
    """
    The flows of the method: a caller signs up and in by a code by mail with
    their flags, which the toggles of the method give while a flow is open.
    """

    CAN_SIGN_UP = 1 << 0
    CAN_SIGN_IN = 1 << 1
