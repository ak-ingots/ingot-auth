"""The storage of the profiles in memory."""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryProfileStorage",
    "AuthMemoryTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.profile import AuthProfileStorage

from .attrs import AuthMemoryAttrsStorage
from .tags import AuthMemoryTagsStorage


class AuthMemoryProfileStorage(AuthProfileStorage):
    """The storage of the profiles in memory."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)
