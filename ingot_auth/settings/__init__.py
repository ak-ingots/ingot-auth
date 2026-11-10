"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("AuthSettingsUnit",)

from ingots.defaults.settings import SettingsUnit
from ingots.puer import Slot

from .configs import AuthConfigs


class AuthSettingsUnit(SettingsUnit):
    """The settings unit, with the addon's :class:`AuthConfigs`."""

    configs = Slot(AuthConfigs)
