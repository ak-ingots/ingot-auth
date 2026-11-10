"""A registry in MongoDB."""

__all__ = ("AuthMongoDbRegistryStorage",)

import abc
import typing as t

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from ingot_auth.registry import (
    AuthItem,
    AuthItemConflictError,
    AuthItemNotFoundError,
    BaseAuthRegistryStorage,
)

from .collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from .collection import Document


class AuthMongoDbRegistryStorage[ItemType: AuthItem](
    AuthMongoDbCollectionMixin, BaseAuthRegistryStorage[ItemType]
):
    """
    A registry in a collection of MongoDB: a document per item, its ``_id`` the
    id of the item, which holds the id unique. A deleted item stays as a document
    marked ``deleted``, which keeps its id taken, and a unique index over the
    documents not marked holds the names unique and frees the name of a deleted
    one.
    """

    @t.override
    async def _create(self, item: ItemType) -> None:
        collection = await self._mongodb_get_collection()
        document = self._build_document(item)
        try:
            await collection.insert_one(
                {**document, "_id": item.id, "deleted": False},
                session=self._mongodb_get_session(),
            )
        except DuplicateKeyError as error:
            details = error.details or {}
            if "_id" in details.get("keyPattern", {}):
                raise AuthItemConflictError.for_id(self.REGISTRY, item.id) from error
            raise AuthItemConflictError.for_name(self.REGISTRY, item.name) from error

    @t.override
    async def _get_all(self) -> tuple[ItemType, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"deleted": False}, session=self._mongodb_get_session()
        ).sort("_id", 1)
        return tuple([self._build_item(document) async for document in documents])

    @t.override
    async def _rename(self, item_id: int, name: str) -> ItemType:
        collection = await self._mongodb_get_collection()
        try:
            document = await collection.find_one_and_update(
                {"_id": item_id, "deleted": False},
                {"$set": {"name": name}},
                return_document=ReturnDocument.AFTER,
                session=self._mongodb_get_session(),
            )
        except DuplicateKeyError as error:
            raise AuthItemConflictError.for_name(self.REGISTRY, name) from error
        if document is None:
            raise AuthItemNotFoundError.for_id(self.REGISTRY, item_id)
        return self._build_item(document)

    @t.override
    async def _delete(self, item_id: int) -> None:
        collection = await self._mongodb_get_collection()
        result = await collection.update_one(
            {"_id": item_id, "deleted": False},
            {"$set": {"deleted": True}},
            session=self._mongodb_get_session(),
        )
        if not result.matched_count:
            raise AuthItemNotFoundError.for_id(self.REGISTRY, item_id)

    @abc.abstractmethod
    def _build_document(self, item: ItemType) -> "Document":
        """The fields of a document for an item, but for its id and the mark."""
        raise NotImplementedError(f"{type(self).__qualname__}._build_document")

    @abc.abstractmethod
    def _build_item(self, document: "Document") -> ItemType:
        raise NotImplementedError(f"{type(self).__qualname__}._build_item")

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index(
            "name", unique=True, partialFilterExpression={"deleted": False}
        )
