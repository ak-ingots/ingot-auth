"""The permissions of the method of a nickname and a password."""

__all__ = ("AuthNicknamePermissions",)

from ingots.defaults.operations import PermissionFlags


class AuthNicknamePermissions(PermissionFlags):
    """
    The flows of the method: a caller signs up and in by a nickname with
    their flags, which the toggles of the method give while a flow is open.
    """

    CAN_SIGN_UP = 1 << 0
    CAN_SIGN_IN = 1 << 1
