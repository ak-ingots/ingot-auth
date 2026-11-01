"""The attributes in MongoDB."""

__all__ = ("AuthMongoDbAttrsStorage",)

import typing as t

from ingot_auth.attrs import AuthAttr, AuthAttrType, BaseAuthAttrsStorage

from .registry import AuthMongoDbRegistryStorage

if t.TYPE_CHECKING:
    from .registry import Document


class AuthMongoDbAttrsStorage(
    AuthMongoDbRegistryStorage[AuthAttr], BaseAuthAttrsStorage
):
    """The attributes in MongoDB."""

    COLLECTION: t.ClassVar[str] = "auth_attrs"

    @t.override
    def _build_document(self, item: AuthAttr) -> "Document":
        return {"name": item.name, "type": item.type.value}

    @t.override
    def _build_item(self, document: "Document") -> AuthAttr:
        return AuthAttr(
            id=document["_id"],
            name=document["name"],
            type=AuthAttrType(document["type"]),
        )
