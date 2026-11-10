"""The tags in MongoDB."""

__all__ = ("AuthMongoDbTagsStorage",)

import typing as t

from ingot_auth.profiles.tags import AuthTag, BaseAuthTagsStorage

from ..registry import AuthMongoDbRegistryStorage

if t.TYPE_CHECKING:
    from ..collection import Document


class AuthMongoDbTagsStorage(AuthMongoDbRegistryStorage[AuthTag], BaseAuthTagsStorage):
    """The tags in MongoDB."""

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_profiles_tags"

    @t.override
    def _build_document(self, item: AuthTag) -> "Document":
        return {"name": item.name}

    @t.override
    def _build_item(self, document: "Document") -> AuthTag:
        return AuthTag(id=document["_id"], name=document["name"])
