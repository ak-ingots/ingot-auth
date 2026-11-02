"""
The storage in MongoDB, with the extra ``pymongo``, on a client of ingot-pymongo:
a project joining ``MongoDbProject`` declares it in the slot of its auth,
``storage = Slot(AuthMongoDbStorage)``. A subclass of a registry changes what it
chooses: the client by a hook, the names of the database and the collection.
"""

__all__ = (
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbProfileStorage",
    "AuthMongoDbRegistryStorage",
    "AuthMongoDbSessionAttrsStorage",
    "AuthMongoDbSessionStorage",
    "AuthMongoDbStorage",
    "AuthMongoDbTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .profile import (
    AuthMongoDbAttrsStorage,
    AuthMongoDbProfileStorage,
    AuthMongoDbTagsStorage,
)
from .registry import AuthMongoDbRegistryStorage
from .session import AuthMongoDbSessionAttrsStorage, AuthMongoDbSessionStorage


class AuthMongoDbStorage(AuthStorage):
    """The storage of the auth in MongoDB."""

    profile = Slot(AuthMongoDbProfileStorage)
    session = Slot(AuthMongoDbSessionStorage)
