"""
The sessions: the registry of the attributes of what a sign-up, a sign-in
happened on, the presets asking for them, and their storage. The sessions
themselves come here too.
"""

__all__ = ("AuthSessionsStorage", "AuthSessionsUnit")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .attrs import AuthSessionAttrsUnit
from .presets import AuthSessionPresetsUnit
from .storage import AuthSessionsStorage


class AuthSessionsUnit(CliUnit):
    """The sessions: the registries of their attributes and of the presets."""

    cli_name = "sessions"
    cli_description = "The sessions of the users."

    attrs = Slot(AuthSessionAttrsUnit)
    presets = Slot(AuthSessionPresetsUnit)
