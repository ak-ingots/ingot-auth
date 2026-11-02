"""The presets of the sessions in MongoDB."""

__all__ = ("AuthMongoDbSessionPresetsStorage",)

import typing as t

from ingot_auth.registry import AuthItemNotFoundError
from ingot_auth.session.presets import (
    AuthSessionPreset,
    AuthSessionPresetBinding,
    BaseAuthSessionPresetsStorage,
)

from ..registry import AuthMongoDbRegistryStorage

if t.TYPE_CHECKING:
    from ..registry import Document


class AuthMongoDbSessionPresetsStorage(
    AuthMongoDbRegistryStorage[AuthSessionPreset], BaseAuthSessionPresetsStorage
):
    """
    The presets of the sessions in MongoDB: the bindings of a preset are in
    its document, ``bindings``, so they go with it, and a binding changes in
    one update of one document.
    """

    COLLECTION: t.ClassVar[str] = "auth_session_presets"

    @t.override
    def _build_document(self, item: AuthSessionPreset) -> "Document":
        return {"name": item.name, "bindings": []}

    @t.override
    def _build_item(self, document: "Document") -> AuthSessionPreset:
        return AuthSessionPreset(id=document["_id"], name=document["name"])

    @t.override
    async def _bind(self, binding: AuthSessionPresetBinding) -> None:
        collection = await self._get_collection()
        others = {
            "$filter": {
                "input": "$bindings",
                "cond": {"$ne": ["$$this.attr_id", binding.attr_id]},
            }
        }
        bound = {"attr_id": binding.attr_id, "required": binding.required}
        result = await collection.update_one(
            {"_id": binding.preset_id, "deleted": False},
            [{"$set": {"bindings": {"$concatArrays": [others, [bound]]}}}],
        )
        if not result.matched_count:
            raise AuthItemNotFoundError.for_id(self.REGISTRY, binding.preset_id)

    @t.override
    async def _unbind(self, preset_id: int, attr_id: int) -> None:
        collection = await self._get_collection()
        result = await collection.update_one(
            {"_id": preset_id, "deleted": False, "bindings.attr_id": attr_id},
            {"$pull": {"bindings": {"attr_id": attr_id}}},
        )
        if result.matched_count:
            return
        if await collection.count_documents({"_id": preset_id, "deleted": False}):
            raise AuthItemNotFoundError.for_binding(self.REGISTRY, preset_id, attr_id)
        raise AuthItemNotFoundError.for_id(self.REGISTRY, preset_id)

    @t.override
    async def _get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        collection = await self._get_collection()
        documents = collection.find({"deleted": False}, {"bindings": True}).sort(
            "_id", 1
        )
        return tuple(
            [
                AuthSessionPresetBinding(
                    preset_id=document["_id"],
                    attr_id=bound["attr_id"],
                    required=bound["required"],
                )
                async for document in documents
                for bound in sorted(document["bindings"], key=lambda b: b["attr_id"])
            ]
        )
