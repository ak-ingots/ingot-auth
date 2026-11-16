"""The configs of the addon, named ``AUTH_*``."""

__all__ = ("AuthConfigs",)

import logging

from ingots.defaults.settings.configs import (
    BoolConfig,
    FloatConfig,
    IntConfig,
    LogLevelConfig,
)
from ingot_mail.settings.configs import MailConfigs


class AuthConfigs(MailConfigs):
    """The configs of the defaults and of the mail with those of the addon."""

    AUTH_LOGGING_LEVEL = LogLevelConfig(logging.INFO)
    AUTH_ATTEMPT_TTL = IntConfig(600)  # seconds an attempt waits for an answer
    AUTH_ATTEMPT_MAX_FAILURES = IntConfig(5)  # answers refused before it is over
    AUTH_SESSION_TTL = IntConfig(30 * 86400)  # seconds a fixed lifetime lasts
    AUTH_SESSION_IDLE_TTL = IntConfig(3600)  # seconds a sliding one idles
    AUTH_SESSION_TOUCH_INTERVAL = IntConfig(300)  # seconds between its writes
    AUTH_SESSION_CACHE_TTL = IntConfig(300)  # seconds a session, a caller is cached
    AUTH_SIGN_UP_ENABLED = BoolConfig(True)  # the sign-up by every method open
    AUTH_SIGN_IN_MIN_DURATION = FloatConfig(0.3)  # seconds of the floor timing
