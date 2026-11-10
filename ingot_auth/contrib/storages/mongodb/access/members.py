"""The memberships in MongoDB."""

__all__ = ("AuthMongoDbMembersStorage",)

import typing as t

from ingot_auth.access.members import AuthMembership, BaseAuthMembersStorage

from ..collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..collection import Document


class AuthMongoDbMembersStorage(AuthMongoDbCollectionMixin, BaseAuthMembersStorage):
    """
    The memberships in MongoDB: a document a membership, a unique index over the
    group and the uid holding it once and giving the uids of a group sorted, one
    over the uid and the group giving the groups of a uid.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_access_members"

    @t.override
    async def _add(self, membership: AuthMembership) -> None:
        collection = await self._mongodb_get_collection()
        document = {"group": membership.group, "uid": membership.uid}
        await collection.replace_one(
            document, document, upsert=True, session=self._mongodb_get_session()
        )

    @t.override
    async def _remove(self, membership: AuthMembership) -> None:
        collection = await self._mongodb_get_collection()
        await collection.delete_one(
            {"group": membership.group, "uid": membership.uid},
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _get_uids(self, group: str) -> tuple[str, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"group": group}, {"uid": True}, session=self._mongodb_get_session()
        ).sort("uid", 1)
        return tuple([document["uid"] async for document in documents])

    @t.override
    async def _get_groups(self, uid: str) -> tuple[str, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"uid": uid}, {"group": True}, session=self._mongodb_get_session()
        ).sort("group", 1)
        return tuple([document["group"] async for document in documents])

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index([("group", 1), ("uid", 1)], unique=True)
        await collection.create_index([("uid", 1), ("group", 1)])
