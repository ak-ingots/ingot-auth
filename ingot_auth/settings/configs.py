"""The configs of the addon, named ``AUTH_*``."""

__all__ = ("AuthConfigs",)

import logging

from ingots.defaults.settings.configs import Configs, LogLevelConfig


class AuthConfigs(Configs):
    """The configs of the defaults with those of the addon."""

    AUTH_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
