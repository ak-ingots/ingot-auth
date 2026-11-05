"""The storage of the profiles in MongoDB."""

__all__ = (
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbProfilesStorage",
    "AuthMongoDbTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.profiles import AuthProfilesStorage

from .attrs import AuthMongoDbAttrsStorage
from .tags import AuthMongoDbTagsStorage


class AuthMongoDbProfilesStorage(AuthProfilesStorage):
    """
    The storage of the profiles in MongoDB: the registries so far, the
    profiles themselves to come with their identities and secrets.
    """

    tags = Slot(AuthMongoDbTagsStorage)
    attrs = Slot(AuthMongoDbAttrsStorage)
