"""
The profiles: the registries of what they hold, the tags and the attributes,
the profiles themselves with their identities, and their storage.
"""

__all__ = (
    "AuthProfile",
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
    "AuthProfilesUnit",
    "AuthProfilesStorage",
)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .attrs import AuthAttrsUnit
from .errors import AuthProfileConflictError, AuthProfileError, AuthProfileNotFoundError
from .items import AuthProfile
from .storage import AuthProfilesStorage
from .tags import AuthTagsUnit


class AuthProfilesUnit(CliUnit):
    """The profiles: the registries of the tags and of the attributes."""

    cli_name = "profiles"
    cli_description = "The profiles of the users."

    tags = Slot(AuthTagsUnit)
    attrs = Slot(AuthAttrsUnit)
