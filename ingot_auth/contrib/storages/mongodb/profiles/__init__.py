"""The storage of the profiles in MongoDB."""

__all__ = (
    "AuthMongoDbAttrsStorage",
    "AuthMongoDbIdentitiesStorage",
    "AuthMongoDbProfilesStorage",
    "AuthMongoDbSecretsStorage",
    "AuthMongoDbTagsStorage",
)

import typing as t

from ingots.puer import Slot
from pymongo.errors import DuplicateKeyError

from ingot_auth.storages import (
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
    AuthProfilesStorage,
)

from ..collection import AuthMongoDbCollectionMixin
from .attrs import AuthMongoDbAttrsStorage
from .identities import AuthMongoDbIdentitiesStorage
from .secrets import AuthMongoDbSecretsStorage
from .tags import AuthMongoDbTagsStorage


class AuthMongoDbProfilesStorage(AuthMongoDbCollectionMixin, AuthProfilesStorage):
    """
    The storage of the profiles in MongoDB: a document a profile, its uid the
    ``_id``, and the storages of its slots.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles"

    tags = Slot(AuthMongoDbTagsStorage)
    attrs = Slot(AuthMongoDbAttrsStorage)
    identities = Slot(AuthMongoDbIdentitiesStorage)
    secrets = Slot(AuthMongoDbSecretsStorage)

    @t.override
    async def _create(self, profile: AuthProfile) -> None:
        collection = await self._mongodb_get_collection()
        try:
            await collection.insert_one(
                {"_id": profile.uid, "created_at": profile.created_at},
                session=self._mongodb_get_session(),
            )
        except DuplicateKeyError as error:
            raise AuthProfileConflictError.for_uid(profile.uid) from error

    @t.override
    async def _get(self, uid: str) -> AuthProfile:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"_id": uid}, session=self._mongodb_get_session()
        )
        if document is None:
            raise AuthProfileNotFoundError.for_uid(uid)
        return AuthProfile(uid=document["_id"], created_at=document["created_at"])
