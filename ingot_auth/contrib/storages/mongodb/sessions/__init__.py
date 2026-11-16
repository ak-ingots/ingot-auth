"""The storage of the sessions in MongoDB."""

__all__ = (
    "AuthMongoDbSessionAttrsStorage",
    "AuthMongoDbSessionPresetsStorage",
    "AuthMongoDbSessionsStorage",
)

import datetime
import typing as t

from ingots.puer import Slot

from ingot_auth.storages import (
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
    AuthSessionsStorage,
)

from ..collection import AuthMongoDbCollectionMixin
from ..values import build_bson_attr_values, build_attr_values
from .attrs import AuthMongoDbSessionAttrsStorage
from .presets import AuthMongoDbSessionPresetsStorage

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..collection import Document


class AuthMongoDbSessionsStorage(AuthMongoDbCollectionMixin, AuthSessionsStorage):
    """
    The storage of the sessions in MongoDB: a document a session, its id the
    ``_id``, a unique index over the hashes of the tokens, which a request
    finds an open one by, and one over the uids, which the open sessions of a
    profile are found by, and one over the open ones by their ids, which a
    sweep pages through; and the storages of its slots.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_sessions"

    attrs = Slot(AuthMongoDbSessionAttrsStorage)
    presets = Slot(AuthMongoDbSessionPresetsStorage)

    @t.override
    async def _open(self, session: AuthSessionRecord) -> None:
        collection = await self._mongodb_get_collection()
        await collection.insert_one(
            {
                "_id": session.uid,
                "profile_uid": session.profile_uid,
                "method": session.method,
                "token_hash": session.token_hash,
                "attr_values": build_bson_attr_values(session.attr_values),
                "opened_at": session.opened_at,
                "seen_at": session.seen_at,
                "closed_at": None,
                "close_reason": None,
            },
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _find(self, token_hash: str) -> AuthSessionRecord:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"token_hash": token_hash, "closed_at": None},
            session=self._mongodb_get_session(),
        )
        if document is None:
            raise AuthSessionNotFoundError.for_token()
        return _build_session(document)

    @t.override
    async def _get_open(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"profile_uid": uid, "closed_at": None}, session=self._mongodb_get_session()
        ).sort([("opened_at", 1), ("_id", 1)])
        return tuple([_build_session(document) async for document in documents])

    @t.override
    async def _get_all(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"profile_uid": uid}, session=self._mongodb_get_session()
        ).sort([("opened_at", 1), ("_id", 1)])
        return tuple([_build_session(document) async for document in documents])

    @t.override
    async def _get_all_open(
        self, after: str | None, limit: int
    ) -> tuple[AuthSessionRecord, ...]:
        collection = await self._mongodb_get_collection()
        query: "Document" = {"closed_at": None}
        if after is not None:
            query["_id"] = {"$gt": after}
        documents = (
            collection.find(query, session=self._mongodb_get_session())
            .sort("_id", 1)
            .limit(limit)
        )
        return tuple([_build_session(document) async for document in documents])

    @t.override
    async def _touch(self, session_uid: str, seen_at: datetime.datetime) -> None:
        collection = await self._mongodb_get_collection()
        result = await collection.update_one(
            {"_id": session_uid, "closed_at": None},
            {"$set": {"seen_at": seen_at}},
            session=self._mongodb_get_session(),
        )
        if not result.matched_count:
            raise AuthSessionNotFoundError.for_uid(session_uid)

    @t.override
    async def _close(
        self,
        session_uid: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        collection = await self._mongodb_get_collection()
        changes = {"closed_at": closed_at, "close_reason": reason.value}
        result = await collection.update_one(
            {"_id": session_uid, "closed_at": None},
            {"$set": changes},
            session=self._mongodb_get_session(),
        )
        if not result.matched_count:
            raise AuthSessionNotFoundError.for_uid(session_uid)

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index("token_hash", unique=True)
        await collection.create_index([("profile_uid", 1), ("closed_at", 1)])
        await collection.create_index([("closed_at", 1), ("_id", 1)])


def _build_session(document: "Document") -> AuthSessionRecord:
    close_reason = document.get("close_reason")
    return AuthSessionRecord(
        uid=document["_id"],
        profile_uid=document["profile_uid"],
        method=document["method"],
        token_hash=document["token_hash"],
        attr_values=build_attr_values(document["attr_values"]),
        opened_at=document["opened_at"],
        seen_at=document["seen_at"],
        closed_at=document.get("closed_at"),
        close_reason=close_reason and AuthSessionCloseReason(close_reason),
    )
