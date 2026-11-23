"""The logging unit of the defaults with the logger of the addon."""

__all__ = ("AuthLoggingUnit",)

import typing as t

from ingot_mail.logging import MailLoggingUnit

if t.TYPE_CHECKING:
    from .project import AuthProject


class AuthLoggingUnit(MailLoggingUnit):
    """
    The logging unit of the mail, with the logger of the addon,
    ``ingot_auth``, at ``AUTH_LOGGING_LEVEL``.
    """

    project: "AuthProject"

    @t.override
    def build_loggers(self) -> dict[str, dict[str, t.Any]]:
        level = self.project.settings.configs.AUTH_LOGGING_LEVEL
        addon = {"level": level, "handlers": ["default"], "propagate": False}
        return {**super().build_loggers(), "ingot_auth": addon}
