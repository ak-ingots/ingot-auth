"""The activity log in MongoDB."""

__all__ = ("AuthMongoDbActivitiesStorage",)

import decimal
import typing as t

import bson

from ingot_auth.storages import (
    AuthActivityAction,
    AuthActivityQuery,
    AuthActivityRecord,
    BaseAuthActivitiesStorage,
)

from .collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from .collection import Document


class AuthMongoDbActivitiesStorage(
    AuthMongoDbCollectionMixin, BaseAuthActivitiesStorage
):
    """
    The activity log in MongoDB: a document a record, its ``_id`` the order it
    came in; a decimal of a context a ``Decimal128``, given back a decimal.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_activities"

    @t.override
    async def _append(self, record: AuthActivityRecord) -> None:
        collection = await self._mongodb_get_collection()
        await collection.insert_one(
            {
                "who": record.who,
                "session_id": record.session_id,
                "action": record.action.value,
                "entity_type": record.entity_type,
                "entity_id": record.entity_id,
                "context": _build_bson(record.context),
                "run_uid": record.run_uid,
                "when": record.when,
            },
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _find(self, query: AuthActivityQuery) -> tuple[AuthActivityRecord, ...]:
        collection = await self._mongodb_get_collection()
        conditions: dict[str, object] = {
            field: value
            for field, value in (
                ("entity_type", query.entity_type),
                ("entity_id", query.entity_id),
                ("who", query.who),
                ("session_id", query.session_id),
                ("action", query.action and query.action.value),
            )
            if value is not None
        }
        span = {
            operator: moment
            for operator, moment in (("$gte", query.since), ("$lt", query.until))
            if moment is not None
        }
        if span:
            conditions["when"] = span
        documents = (
            collection.find(conditions, session=self._mongodb_get_session())
            .sort([("when", -1), ("_id", -1)])
            .limit(query.limit)
        )
        return tuple([_build_record(document) async for document in documents])

    @t.override
    async def _mongodb_create_indexes(
        self, collection: "AsyncCollection[Document]"
    ) -> None:
        await collection.create_index(
            [("entity_type", 1), ("entity_id", 1), ("when", -1)]
        )
        await collection.create_index([("who", 1), ("when", -1)])
        await collection.create_index([("session_id", 1), ("when", -1)])
        await collection.create_index([("when", -1)])


def _build_record(document: "Document") -> AuthActivityRecord:
    return AuthActivityRecord(
        who=document["who"],
        session_id=document["session_id"],
        action=AuthActivityAction(document["action"]),
        entity_type=document["entity_type"],
        entity_id=document["entity_id"],
        context=t.cast("dict[str, object]", _build_value(document["context"])),
        run_uid=document["run_uid"],
        when=document["when"],
    )


def _build_bson(value: object) -> object:
    if isinstance(value, decimal.Decimal):
        return bson.Decimal128(value)
    if isinstance(value, dict):
        return {key: _build_bson(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_build_bson(item) for item in value]
    return value


def _build_value(value: object) -> object:
    if isinstance(value, bson.Decimal128):
        return value.to_decimal()
    if isinstance(value, dict):
        return {key: _build_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_build_value(item) for item in value]
    return value
