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
from ..values import build_bson_values, build_values
from .attrs import AuthMongoDbSessionAttrsStorage
from .presets import AuthMongoDbSessionPresetsStorage

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..collection import Document


class AuthMongoDbSessionsStorage(AuthMongoDbCollectionMixin, AuthSessionsStorage):
    """
    The storage of the sessions in MongoDB: a document a session, its id the
    ``_id``, a unique index over the hashes of the tokens, which a request
    finds an open one by; and the storages of its slots.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_sessions"

    attrs = Slot(AuthMongoDbSessionAttrsStorage)
    presets = Slot(AuthMongoDbSessionPresetsStorage)

    @t.override
    async def _open(self, session: AuthSessionRecord) -> None:
        collection = await self._mongodb_get_collection()
        await collection.insert_one(
            {
                "_id": session.id,
                "uid": session.uid,
                "method": session.method,
                "token_hash": session.token_hash,
                "values": build_bson_values(session.values),
                "opened_at": session.opened_at,
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
        return AuthSessionRecord(
            id=document["_id"],
            uid=document["uid"],
            method=document["method"],
            token_hash=document["token_hash"],
            values=build_values(document["values"]),
            opened_at=document["opened_at"],
        )

    @t.override
    async def _close(
        self,
        session_id: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        collection = await self._mongodb_get_collection()
        result = await collection.update_one(
            {"_id": session_id, "closed_at": None},
            {"$set": {"closed_at": closed_at, "close_reason": reason.value}},
            session=self._mongodb_get_session(),
        )
        if not result.matched_count:
            raise AuthSessionNotFoundError.for_id(session_id)

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index("token_hash", unique=True)
