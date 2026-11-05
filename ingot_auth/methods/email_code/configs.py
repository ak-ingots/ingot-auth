"""The configs of the method of an email and a code sent to it."""

__all__ = ("AuthEmailCodeConfigs",)

from ingots.defaults.settings.configs import BoolConfig, Configs


class AuthEmailCodeConfigs(Configs):
    """
    The toggles of the flows of the method, on: the slot of the method is the
    choice, a toggle closes a flow in an environment. Mixed into the configs
    of a project that takes the method.
    """

    AUTH_SIGN_UP_EMAIL_CODE_ENABLED = BoolConfig(True)
    AUTH_SIGN_IN_EMAIL_CODE_ENABLED = BoolConfig(True)
