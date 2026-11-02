"""The storage of the profiles in MongoDB."""

__all__ = (
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbProfileStorage",
    "AuthMongoDbTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.profile import AuthProfileStorage

from .attrs import AuthMongoDbAttrsStorage
from .tags import AuthMongoDbTagsStorage


class AuthMongoDbProfileStorage(AuthProfileStorage):
    """The storage of the profiles in MongoDB."""

    tags = Slot(AuthMongoDbTagsStorage)
    attrs = Slot(AuthMongoDbAttrsStorage)
