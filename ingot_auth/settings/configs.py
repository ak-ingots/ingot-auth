"""The configs of the addon, named ``AUTH_*``."""

__all__ = ("AuthConfigs",)

import logging

from ingots.defaults.settings.configs import Configs, IntConfig, LogLevelConfig


class AuthConfigs(Configs):
    """The configs of the defaults with those of the addon."""

    AUTH_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
    AUTH_ATTEMPT_TTL = IntConfig(600)  # seconds an attempt waits for an answer
    AUTH_ATTEMPT_MAX_FAILURES = IntConfig(5)  # answers refused before it is over
