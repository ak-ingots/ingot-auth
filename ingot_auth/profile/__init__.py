"""
The profiles: the registries of what they hold, the tags and the attributes,
and their storage. What else is of the profiles comes here too.
"""

__all__ = ("AuthProfileStorage", "AuthProfileUnit")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .attrs import AuthAttrs
from .storage import AuthProfileStorage
from .tags import AuthTags


class AuthProfileUnit(CliUnit):
    """The profiles: the registries of the tags and of the attributes."""

    cli_name = "profile"
    cli_description = "The profiles of the users."

    tags = Slot(AuthTags)
    attrs = Slot(AuthAttrs)
