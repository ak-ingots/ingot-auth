"""
The storage in MongoDB, with the extra ``pymongo``, on a client of ingot-pymongo:
a project joining ``MongoDbProject`` declares it in the slot of its auth,
``storage = Slot(AuthMongoDbStorage)``. A subclass of a storage changes what it
chooses: the client by a hook, the names of the database and the collection.
"""

__all__ = (
    "AuthMongoDbAccessStorage",
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbCollectionMixin",
    "AuthMongoDbIdentitiesStorage",
    "AuthMongoDbMembersStorage",
    "AuthMongoDbProfilesStorage",
    "AuthMongoDbRegistryStorage",
    "AuthMongoDbSecretsStorage",
    "AuthMongoDbSessionAttrsStorage",
    "AuthMongoDbSessionPresetsStorage",
    "AuthMongoDbSessionsStorage",
    "AuthMongoDbSignUpRecordsStorage",
    "AuthMongoDbSignUpStorage",
    "AuthMongoDbStorage",
    "AuthMongoDbTagsStorage",
)

import typing as t

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .access import AuthMongoDbAccessStorage, AuthMongoDbMembersStorage
from .collection import AuthMongoDbCollectionMixin
from .profiles import (
    AuthMongoDbAttrsStorage,
    AuthMongoDbIdentitiesStorage,
    AuthMongoDbProfilesStorage,
    AuthMongoDbSecretsStorage,
    AuthMongoDbTagsStorage,
)
from .registry import AuthMongoDbRegistryStorage
from .sessions import (
    AuthMongoDbSessionAttrsStorage,
    AuthMongoDbSessionPresetsStorage,
    AuthMongoDbSessionsStorage,
)
from .sign_up import AuthMongoDbSignUpRecordsStorage, AuthMongoDbSignUpStorage

if t.TYPE_CHECKING:
    from ingot_pymongo import MongoDbProject
    from ingot_pymongo.mongodb.clients import BaseMongoDbClient
    from pymongo.asynchronous.client_session import AsyncClientSession


class AuthMongoDbStorage(AuthStorage):
    """
    The storage of the auth in MongoDB. A transaction is one of a session of
    the client of :meth:`_get_client`, which the storages pass to their
    queries: MongoDB takes transactions on a replica set only, of one node
    for the tests. A transaction may fail on a conflict with another, with
    the label ``TransientTransactionError``: retrying it is for the caller.
    """

    project: "MongoDbProject"

    profiles = Slot(AuthMongoDbProfilesStorage)
    sessions = Slot(AuthMongoDbSessionsStorage)
    sign_up = Slot(AuthMongoDbSignUpStorage)
    access = Slot(AuthMongoDbAccessStorage)

    @t.override
    async def _begin(self) -> object:
        # a transaction sees the collections there were when it began: those
        # the storages create on their first use are created before it
        for path, slot in type(self).slots_walk():
            if issubclass(slot.cls, AuthMongoDbCollectionMixin):
                storage = self.slots_find_entity(path)
                await t.cast(
                    AuthMongoDbCollectionMixin, storage
                )._mongodb_get_collection()
        client = await self._get_client()
        session = client.client.start_session()
        await session.start_transaction()
        return session

    @t.override
    async def _commit(self, transaction: object) -> None:
        session = t.cast("AsyncClientSession", transaction)
        try:
            await session.commit_transaction()
        finally:
            await session.end_session()

    @t.override
    async def _rollback(self, transaction: object) -> None:
        session = t.cast("AsyncClientSession", transaction)
        try:
            await session.abort_transaction()
        finally:
            await session.end_session()

    def _get_client(self) -> "BaseMongoDbClient":
        """The client of the transactions, that of the storages by default."""
        return self.project.mongodb.clients.default
