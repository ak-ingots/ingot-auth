"""
The command line of the auth, the domain of its commands: the group
``auth``, a package or a module of it for each group of the domains, as
the tree goes, ``profiles/tags.py`` the commands of ``auth profiles tags``.
"""

__all__ = ("AuthCliUnit", "AuthCommandsUnit")

from ingots.defaults.cli import CliUnit, CommandsUnit
from ingots.puer import Slot

from .access import AuthAccessCommandsUnit
from .activities import AuthActivitiesCommandsUnit
from .profiles import AuthProfilesCommandsUnit
from .sessions import AuthSessionsCommandsUnit


class AuthCommandsUnit(CommandsUnit):
    cli_description = "The auth of the users."
    profiles = Slot(AuthProfilesCommandsUnit)
    sessions = Slot(AuthSessionsCommandsUnit)
    access = Slot(AuthAccessCommandsUnit)
    activities = Slot(AuthActivitiesCommandsUnit)


class AuthCliUnit(CliUnit):
    """
    The command line of the defaults and ``auth``; an application of other
    addons with commands joins it with theirs:
    ``AppCliUnit(AuthCliUnit, GrpcCliUnit)``.
    """

    auth = Slot(AuthCommandsUnit)
