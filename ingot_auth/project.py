"""The project of the addon: what an application inherits from."""

__all__ = ("AuthProject",)

from ingots.defaults import Project
from ingots.puer import Slot

from .auth import AuthUnit
from .logging import AuthLogging
from .settings import AuthSettings


class AuthProject(Project):
    """
    The project of the defaults with the addon's :class:`AuthSettings`,
    :class:`AuthLogging` and the auth, :class:`AuthUnit`. An application
    inherits from it and sets its own ``env_configs_prefix``; the addon run on
    its own (``python -m ingot_auth``) keeps the prefix of the defaults,
    ``INGOT``.
    """

    settings = Slot(AuthSettings)
    logging = Slot(AuthLogging)
    auth = Slot(AuthUnit)
