"""The storage of the profiles in memory."""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryIdentitiesStorage",
    "AuthMemoryProfileStorage",
    "AuthMemoryProfilesStorage",
    "AuthMemoryTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.profile import AuthProfileStorage

from .attrs import AuthMemoryAttrsStorage
from .identities import AuthMemoryIdentitiesStorage
from .profiles import AuthMemoryProfilesStorage
from .tags import AuthMemoryTagsStorage


class AuthMemoryProfileStorage(AuthProfileStorage):
    """The storage of the profiles in memory."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)
    profiles = Slot(AuthMemoryProfilesStorage)
    identities = Slot(AuthMemoryIdentitiesStorage)
