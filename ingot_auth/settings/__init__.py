"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("AuthSettings",)

from ingots.defaults.settings import Settings
from ingots.puer import Slot

from .configs import AuthConfigs


class AuthSettings(Settings):
    """The settings unit, with the addon's :class:`AuthConfigs`."""

    configs = Slot(AuthConfigs)
