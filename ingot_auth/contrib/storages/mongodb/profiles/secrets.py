"""The secrets in MongoDB."""

__all__ = ("AuthMongoDbSecretsStorage",)

import typing as t

from ingot_auth.profiles.secrets import AuthSecretNotFoundError, BaseAuthSecretsStorage

from ..collection import AuthMongoDbCollectionMixin


class AuthMongoDbSecretsStorage(AuthMongoDbCollectionMixin, BaseAuthSecretsStorage):
    """
    The secrets in MongoDB: a document a secret, the uid of its profile the
    ``_id``, which a new one replaces.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles_secrets"

    @t.override
    async def _put(self, uid: str, secret: str) -> None:
        collection = await self._mongodb_get_collection()
        await collection.replace_one(
            {"_id": uid},
            {"_id": uid, "secret": secret},
            upsert=True,
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _get(self, uid: str) -> str:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"_id": uid}, session=self._mongodb_get_session()
        )
        if document is None:
            raise AuthSecretNotFoundError.for_uid(uid)
        return t.cast(str, document["secret"])
