"""
The profiles: the registries of what they hold, the tags and the attributes.
The profiles themselves, their identities and their secrets are kept by the
storages, :mod:`ingot_auth.storages`.
"""

__all__ = ("AuthProfilesUnit",)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .attrs import AuthAttrsUnit
from .tags import AuthTagsUnit


class AuthProfilesUnit(CliUnit):
    """The profiles: the registries of the tags and of the attributes."""

    cli_name = "profiles"
    cli_description = "The profiles of the users."

    tags = Slot(AuthTagsUnit)
    attrs = Slot(AuthAttrsUnit)
