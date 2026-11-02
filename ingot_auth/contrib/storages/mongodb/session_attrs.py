"""The attributes of the sessions in MongoDB."""

__all__ = ("AuthMongoDbSessionAttrsStorage",)

import typing as t

from ingot_auth.attrs import AuthAttrType
from ingot_auth.session_attrs import (
    AuthSessionAttr,
    AuthSessionAttrSource,
    BaseAuthSessionAttrsStorage,
)

from .registry import AuthMongoDbRegistryStorage

if t.TYPE_CHECKING:
    from .registry import Document


class AuthMongoDbSessionAttrsStorage(
    AuthMongoDbRegistryStorage[AuthSessionAttr], BaseAuthSessionAttrsStorage
):
    """The attributes of the sessions in MongoDB."""

    COLLECTION: t.ClassVar[str] = "auth_session_attrs"

    @t.override
    def _build_document(self, item: AuthSessionAttr) -> "Document":
        return {
            "name": item.name,
            "type": item.type.value,
            "source": item.source.value,
        }

    @t.override
    def _build_item(self, document: "Document") -> AuthSessionAttr:
        return AuthSessionAttr(
            id=document["_id"],
            name=document["name"],
            type=AuthAttrType(document["type"]),
            source=AuthSessionAttrSource(document["source"]),
        )
