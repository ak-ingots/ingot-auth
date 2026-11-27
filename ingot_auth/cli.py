"""
The command line of the auth: the group ``auth`` of the commands of its
domains, each beside the commands of its package, put together here, where
none of them imports another.
"""

__all__ = (
    "AuthAccessCommandsUnit",
    "AuthCliUnit",
    "AuthCommandsUnit",
    "AuthProfilesCommandsUnit",
)

from ingots.defaults.cli import CliUnit, CommandsUnit
from ingots.puer import Slot

from .access.groups.commands import AuthGroupsCommandsUnit
from .access.members.commands import AuthMembersCommandsUnit
from .activities.commands import AuthActivitiesCommandsUnit
from .profiles.attrs.commands import AuthAttrsCommandsUnit
from .profiles.tags.commands import AuthTagsCommandsUnit
from .sessions.commands import AuthSessionsCommandsUnit


class AuthProfilesCommandsUnit(CommandsUnit):
    cli_description = "The profiles of the users."
    tags = Slot(AuthTagsCommandsUnit)
    attrs = Slot(AuthAttrsCommandsUnit)


class AuthAccessCommandsUnit(CommandsUnit):
    cli_description = "The groups of the users and their members."
    groups = Slot(AuthGroupsCommandsUnit)
    members = Slot(AuthMembersCommandsUnit)


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
