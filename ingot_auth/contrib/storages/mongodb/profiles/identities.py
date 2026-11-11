"""The identities in MongoDB."""

__all__ = ("AuthMongoDbIdentitiesStorage",)

import typing as t

from pymongo.errors import DuplicateKeyError

from ingot_auth.storages import (
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    BaseAuthIdentitiesStorage,
)

from ..collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..collection import Document


class AuthMongoDbIdentitiesStorage(
    AuthMongoDbCollectionMixin, BaseAuthIdentitiesStorage
):
    """
    The identities in MongoDB: a document an identity, a unique index over the
    kind and the value holding an identifier bound once.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles_identities"

    @t.override
    async def _create(self, identity: AuthIdentity) -> None:
        collection = await self._mongodb_get_collection()
        try:
            await collection.insert_one(
                {"kind": identity.kind, "value": identity.value, "uid": identity.uid},
                session=self._mongodb_get_session(),
            )
        except DuplicateKeyError as error:
            raise AuthIdentityConflictError.for_kind(identity.kind) from error

    @t.override
    async def _find_uid(self, kind: str, value: str) -> str:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"kind": kind, "value": value}, session=self._mongodb_get_session()
        )
        if document is None:
            raise AuthIdentityNotFoundError.for_kind(kind)
        return t.cast(str, document["uid"])

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index([("kind", 1), ("value", 1)], unique=True)
