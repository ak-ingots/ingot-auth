"""
The storage in memory: for the tests and the addon run on its own. What it
stores is gone with the project. An application declares it in the slot of
its auth: ``storage = Slot(AuthMemoryStorage)``.
"""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryRegistryStorage",
    "AuthMemoryStorage",
    "AuthMemoryTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .attrs import AuthMemoryAttrsStorage
from .registry import AuthMemoryRegistryStorage
from .tags import AuthMemoryTagsStorage


class AuthMemoryStorage(AuthStorage):
    """The storage of the auth in memory."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)
