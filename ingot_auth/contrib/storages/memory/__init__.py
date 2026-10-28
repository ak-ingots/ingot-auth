"""
The storage in memory: for the tests and the addon run on its own. What it
stores is gone with the project.
"""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryProject",
    "AuthMemoryRegistryStorage",
    "AuthMemoryStorage",
    "AuthMemoryTagsStorage",
    "AuthMemoryUnit",
)

from ingots.puer import Slot

from ingot_auth.auth import AuthUnit
from ingot_auth.project import AuthProject
from ingot_auth.storage import AuthStorage

from .attrs import AuthMemoryAttrsStorage
from .registry import AuthMemoryRegistryStorage
from .tags import AuthMemoryTagsStorage


class AuthMemoryStorage(AuthStorage):
    """The storage of the auth in memory."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)


class AuthMemoryUnit(AuthUnit):
    """The auth with the storage in memory."""

    storage = Slot(AuthMemoryStorage)


class AuthMemoryProject(AuthProject):
    """The project of the addon with the storage in memory."""

    auth = Slot(AuthMemoryUnit)
