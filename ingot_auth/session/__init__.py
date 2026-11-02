"""
The sessions: the registry of the attributes of what a sign-up, a sign-in
happened on, the presets asking for them, and their storage. The sessions
themselves come here too.
"""

__all__ = ("AuthSessionStorage", "AuthSessionUnit")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .attrs import AuthSessionAttrs
from .presets import AuthSessionPresets
from .storage import AuthSessionStorage


class AuthSessionUnit(CliUnit):
    """The sessions: the registries of their attributes and of the presets."""

    cli_name = "session"
    cli_description = "The sessions of the users."

    attrs = Slot(AuthSessionAttrs)
    presets = Slot(AuthSessionPresets)
