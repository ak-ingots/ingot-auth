"""
The storage in MongoDB, with the extra ``pymongo``, on a client of ingot-pymongo:
a project joining ``MongoDbProject`` declares it in the slot of its auth,
``storage = Slot(AuthMongoDbStorage)``. A subclass of a registry changes what it
chooses: the client by a hook, the names of the database and the collection.
"""

__all__ = (
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbRegistryStorage",
    "AuthMongoDbStorage",
    "AuthMongoDbTagsStorage",
)

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .attrs import AuthMongoDbAttrsStorage
from .registry import AuthMongoDbRegistryStorage
from .tags import AuthMongoDbTagsStorage


class AuthMongoDbStorage(AuthStorage):
    """The storage of the auth in MongoDB."""

    tags = Slot(AuthMongoDbTagsStorage)
    attrs = Slot(AuthMongoDbAttrsStorage)
