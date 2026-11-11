"""The records of the sign-ups in MongoDB."""

__all__ = ("AuthMongoDbSignUpRecordsStorage",)

import typing as t

from ingot_auth.storages import (
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    BaseAuthSignUpRecordsStorage,
)

from ..collection import AuthMongoDbCollectionMixin
from ..values import build_bson_attr_values, build_attr_values


class AuthMongoDbSignUpRecordsStorage(
    AuthMongoDbCollectionMixin, BaseAuthSignUpRecordsStorage
):
    """
    The records of the sign-ups in MongoDB: a document a record, the uid of its
    profile the ``_id``, its ``attr_values`` as :func:`build_bson_attr_values`
    gives them.
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
                "attr_values": build_bson_attr_values(record.attr_values),
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
            attr_values=build_attr_values(document["attr_values"]),
        )
