"""
The storage in memory: for the tests and the addon run on its own. What it
stores is gone with the project. An application declares it in the slot of
its auth: ``storage = Slot(AuthMemoryStorage)``.
"""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryIdentitiesStorage",
    "AuthMemoryProfileStorage",
    "AuthMemoryProfilesStorage",
    "AuthMemoryRegistryStorage",
    "AuthMemorySessionAttrsStorage",
    "AuthMemorySessionPresetsStorage",
    "AuthMemorySessionStorage",
    "AuthMemorySignUpRecordsStorage",
    "AuthMemorySignUpStorage",
    "AuthMemoryStorage",
    "AuthMemoryTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .profile import (
    AuthMemoryAttrsStorage,
    AuthMemoryIdentitiesStorage,
    AuthMemoryProfilesStorage,
    AuthMemoryProfileStorage,
    AuthMemoryTagsStorage,
)
from .registry import AuthMemoryRegistryStorage
from .session import (
    AuthMemorySessionAttrsStorage,
    AuthMemorySessionPresetsStorage,
    AuthMemorySessionStorage,
)
from .sign_up import AuthMemorySignUpRecordsStorage, AuthMemorySignUpStorage


class AuthMemoryStorage(AuthStorage):
    """The storage of the auth in memory."""

    profile = Slot(AuthMemoryProfileStorage)
    session = Slot(AuthMemorySessionStorage)
    sign_up = Slot(AuthMemorySignUpStorage)
