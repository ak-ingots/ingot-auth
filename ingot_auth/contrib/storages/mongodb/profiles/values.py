"""The values of the profiles in MongoDB."""

__all__ = ("AuthMongoDbProfileValuesStorage",)

import typing as t

from ingot_auth.storages import AuthProfileValues, BaseAuthProfileValuesStorage

from ..collection import AuthMongoDbCollectionMixin
from ..values import build_attr_values, build_bson_attr_values

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


class AuthMongoDbProfileValuesStorage(
    AuthMongoDbCollectionMixin, BaseAuthProfileValuesStorage
):
    """
    The values of the profiles in MongoDB: a document a profile, its uid the
    ``_id``, the ids of its tags and the values of its attributes.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles_values"

    @t.override
    async def _get(self, uid: str) -> AuthProfileValues:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"_id": uid}, session=self._mongodb_get_session()
        )
        if document is None:
            return AuthProfileValues()
        return AuthProfileValues(
            tag_uids=frozenset(document.get("tag_uids", ())),
            attr_values=build_attr_values(document.get("attr_values", [])),
        )

    @t.override
    async def _set_tags(self, uid: str, tag_uids: frozenset[int]) -> None:
        await self._set(uid, "tag_uids", sorted(tag_uids))

    @t.override
    async def _set_attr_values(
        self, uid: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> None:
        await self._set(uid, "attr_values", build_bson_attr_values(attr_values))

    async def _set(self, uid: str, field: str, value: object) -> None:
        collection = await self._mongodb_get_collection()
        await collection.update_one(
            {"_id": uid},
            {"$set": {field: value}},
            upsert=True,
            session=self._mongodb_get_session(),
        )
