"""A storage in a collection of MongoDB."""

__all__ = ("AuthMongoDbCollectionMixin", "Document")

import datetime
import typing as t

from bson.codec_options import CodecOptions
from pymongo.errors import CollectionInvalid

if t.TYPE_CHECKING:
    from ingot_pymongo import MongoDbProject
    from ingot_pymongo.mongodb.clients import BaseMongoDbClient
    from pymongo.asynchronous.client_session import AsyncClientSession
    from pymongo.asynchronous.collection import AsyncCollection

    from ingot_auth.project import AuthProject

Document: t.TypeAlias = dict[str, t.Any]
"""A document of a collection, as the client of ingot-pymongo gives it."""

# a time comes back as it is given to a storage: aware, in UTC
CODEC_OPTIONS: t.Final[CodecOptions[t.Any]] = CodecOptions(
    tz_aware=True, tzinfo=datetime.UTC
)


class AuthMongoDbCollectionMixin:
    """
    A storage in a collection of MongoDB, on a client of ingot-pymongo: the
    collection is created with its indexes on its first use, and a query takes
    the session of the transaction of :class:`AuthMongoDbStorage` in the current
    context, if any.
    """

    # the database and the collection of the client of _mongodb_get_client()
    MONGODB_DATABASE: t.ClassVar[str] = "ingot_auth"
    MONGODB_COLLECTION: t.ClassVar[str]

    project: "MongoDbProject"
    _mongodb_collection: "AsyncCollection[Document]"

    @t.final
    async def _mongodb_get_collection(self) -> "AsyncCollection[Document]":
        """The collection, created with its indexes on the first call."""
        try:
            return self._mongodb_collection
        except AttributeError:
            pass
        client = await self._mongodb_get_client()
        database = client.get_database(self.MONGODB_DATABASE)
        try:
            await database.create_collection(self.MONGODB_COLLECTION)
        except CollectionInvalid:
            pass  # created already
        collection = database.get_collection(
            self.MONGODB_COLLECTION, codec_options=CODEC_OPTIONS
        )
        await self._mongodb_create_indexes(collection)
        self._mongodb_collection = collection
        return collection

    @t.final
    def _mongodb_get_session(self) -> "AsyncClientSession | None":
        """The session of the transaction of the storage in this context, if any."""
        storage = t.cast("AuthProject", self.project).auth.storage
        return t.cast("AsyncClientSession | None", storage.get_transaction())

    def _mongodb_get_client(self) -> "BaseMongoDbClient":
        """
        The client of the storage: another one is a matter of an override, and
        it is that of :class:`AuthMongoDbStorage` for a transaction to span the
        storage.
        """
        return self.project.mongodb.clients.default

    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        """The indexes of the collection but that of ``_id``: none by default."""
