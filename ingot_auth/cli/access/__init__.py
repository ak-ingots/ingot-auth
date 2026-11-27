"""The commands of the access, ``auth access``."""

__all__ = ("AuthAccessCommandsUnit",)

from ingots.defaults.cli import CommandsUnit
from ingots.puer import Slot

from .groups import AuthGroupsCommandsUnit
from .members import AuthMembersCommandsUnit


class AuthAccessCommandsUnit(CommandsUnit):
    cli_description = "The groups of the users and their members."
    groups = Slot(AuthGroupsCommandsUnit)
    members = Slot(AuthMembersCommandsUnit)
