"""The settings unit of the defaults with the configs of the addon."""

__all__ = ("AuthSettingsUnit",)

from ingot_mail.settings import MailSettingsUnit
from ingots.puer import Slot

from .configs import AuthConfigs


class AuthSettingsUnit(MailSettingsUnit):
    """The settings unit of the mail, with the addon's :class:`AuthConfigs`."""

    configs = Slot(AuthConfigs)
