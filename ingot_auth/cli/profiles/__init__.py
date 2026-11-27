"""The commands of the profiles, ``auth profiles``."""

__all__ = ("AuthProfilesCommandsUnit",)

from ingots.defaults.cli import CommandsUnit
from ingots.puer import Slot

from .attrs import AuthAttrsCommandsUnit
from .tags import AuthTagsCommandsUnit


class AuthProfilesCommandsUnit(CommandsUnit):
    cli_description = "The profiles of the users."
    tags = Slot(AuthTagsCommandsUnit)
    attrs = Slot(AuthAttrsCommandsUnit)
