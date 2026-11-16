"""The project of the addon: what an application inherits from."""

__all__ = ("AuthProject",)

from ingot_mail import MailProject
from ingots.puer import Slot

from .auth import AuthUnit
from .logging import AuthLoggingUnit
from .operations import AuthOperationsUnit
from .settings import AuthSettingsUnit


class AuthProject(MailProject):
    """
    The project of the mail, ingot-mail's, whose mailer sends the mail of the
    methods, with the addon's :class:`AuthSettingsUnit`,
    :class:`AuthLoggingUnit`, :class:`AuthOperationsUnit`, whose callers give
    the anonymous one what anyone may of the auth, and the auth,
    :class:`AuthUnit`. An application inherits from it and sets its own
    ``env_configs_prefix``; the addon run on its own (``python -m
    ingot_auth``) keeps the prefix of the defaults, ``INGOT``.
    """

    settings = Slot(AuthSettingsUnit)
    logging = Slot(AuthLoggingUnit)
    operations = Slot(AuthOperationsUnit)
    auth = Slot(AuthUnit)
