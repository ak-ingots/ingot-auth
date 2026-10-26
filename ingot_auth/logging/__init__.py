"""The logging unit of the defaults with the logger of the addon."""

__all__ = ("AuthLogging",)

import typing as t

from ingots.defaults.logging import Logging

if t.TYPE_CHECKING:
    from ..project import AuthProject


class AuthLogging(Logging):
    """
    The logging unit, with the logger of the addon, ``ingot_auth``, at
    ``AUTH_LOGGING_LEVEL``.
    """

    project: "AuthProject"

    @t.override
    def build_loggers(self) -> dict[str, dict[str, t.Any]]:
        level = self.project.settings.configs.AUTH_LOGGING_LEVEL
        addon = {"level": level, "handlers": ["default"], "propagate": False}
        return {**super().build_loggers(), "ingot_auth": addon}
