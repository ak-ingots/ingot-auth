"""The records of the sign-ups in MongoDB."""

__all__ = ("AuthMongoDbSignUpRecordsStorage",)

import decimal
import typing as t

from bson.decimal128 import Decimal128

from ingot_auth.sign_up import (
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    BaseAuthSignUpRecordsStorage,
)

from ..collection import AuthMongoDbCollectionMixin

if t.TYPE_CHECKING:
    from ingot_auth.registry import AuthAttrValue


class AuthMongoDbSignUpRecordsStorage(
    AuthMongoDbCollectionMixin, BaseAuthSignUpRecordsStorage
):
    """
    The records of the sign-ups in MongoDB: a document a record, the uid of its
    profile the ``_id``. The values are a list of the ids of their attributes
    with them, as a key of a document is a string; a decimal is a ``Decimal128``
    of BSON, the other types are those of BSON already.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_sign_up_records"

    @t.override
    async def _add(self, record: AuthSignUpRecord) -> None:
        collection = await self._mongodb_get_collection()
        await collection.insert_one(
            {
                "_id": record.uid,
                "method": record.method,
                "signed_up_at": record.signed_up_at,
                "values": [
                    {"attr_id": attr_id, "value": _build_bson_value(value)}
                    for attr_id, value in record.values.items()
                ],
            },
            session=self._mongodb_get_session(),
        )

    @t.override
    async def _get(self, uid: str) -> AuthSignUpRecord:
        collection = await self._mongodb_get_collection()
        document = await collection.find_one(
            {"_id": uid}, session=self._mongodb_get_session()
        )
        if document is None:
            raise AuthSignUpRecordNotFoundError.for_uid(uid)
        return AuthSignUpRecord(
            uid=document["_id"],
            method=document["method"],
            signed_up_at=document["signed_up_at"],
            values={
                bound["attr_id"]: _build_value(bound["value"])
                for bound in document["values"]
            },
        )


def _build_bson_value(value: "AuthAttrValue") -> object:
    return Decimal128(value) if isinstance(value, decimal.Decimal) else value


def _build_value(value: object) -> "AuthAttrValue":
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return t.cast("AuthAttrValue", value)
