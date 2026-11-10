"""The secrets in MongoDB."""

__all__ = ("AuthMongoDbSecretsStorage",)

import typing as t

from ingot_auth.profiles.secrets import AuthSecretNotFoundError, BaseAuthSecretsStorage

from ..collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..collection import Document


class AuthMongoDbSecretsStorage(AuthMongoDbCollectionMixin, BaseAuthSecretsStorage):
    """
    The secrets in MongoDB: a document a secret, a unique index over the method
    and the subject holding one a subject, which a new one replaces.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles_secrets"

    @t.override
    async def _put(self, method: str, subject: str, secret: str) -> None:
        collection = await self._mongodb_get_collection()
        key = {"method": method, "subject": subject}
        await collection.replace_one(
            key,
            {**key, "secret": secret},
            upsert=True,
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _get(self, method: str, subject: str) -> str:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"method": method, "subject": subject},
            session=self._mongodb_get_session(),
        )
        if document is None:
            raise AuthSecretNotFoundError.for_method(method)
        return t.cast(str, document["secret"])

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index([("method", 1), ("subject", 1)], unique=True)
