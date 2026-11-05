"""The configs of the method of a nickname and a password."""

__all__ = ("AuthNicknameConfigs",)

from ingots.defaults.settings.configs import BoolConfig, Configs


class AuthNicknameConfigs(Configs):
    """
    The toggles of the flows of the method, on: the slot of the method is the
    choice, a toggle closes a flow in an environment. Mixed into the configs
    of a project that takes the method.
    """

    AUTH_SIGN_UP_NICKNAME_ENABLED = BoolConfig(True)
    AUTH_SIGN_IN_NICKNAME_ENABLED = BoolConfig(True)
