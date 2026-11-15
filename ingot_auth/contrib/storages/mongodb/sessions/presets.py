"""The presets of the sessions in MongoDB."""

__all__ = ("AuthMongoDbSessionPresetsStorage",)

import typing as t

from ingot_auth.storages import (
    AuthItemNotFoundError,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    BaseAuthSessionPresetsStorage,
)

from ..registry import AuthMongoDbRegistryStorage

if t.TYPE_CHECKING:
    from ..collection import Document


class AuthMongoDbSessionPresetsStorage(
    AuthMongoDbRegistryStorage[AuthSessionPreset], BaseAuthSessionPresetsStorage
):
    """
    The presets of the sessions in MongoDB: the bindings of a preset are in
    its document, ``bindings``, so they go with it, and a binding changes in
    one update of one document.
    """

    MONGODB_COLLECTION: t.ClassVar[str] = "auth_sessions_presets"

    @t.override
    def _build_document(self, item: AuthSessionPreset) -> "Document":
        return {"name": item.name, "bindings": []}

    @t.override
    def _build_item(self, document: "Document") -> AuthSessionPreset:
        return AuthSessionPreset(uid=document["_id"], name=document["name"])

    @t.override
    async def _bind(self, binding: AuthSessionPresetBinding) -> None:
        collection = await self._mongodb_get_collection()
        others = {
            "$filter": {
                "input": "$bindings",
                "cond": {"$ne": ["$$this.attr_uid", binding.attr_uid]},
            }
        }
        bound = {"attr_uid": binding.attr_uid, "required": binding.required}
        result = await collection.update_one(
            {"_id": binding.preset_uid, "deleted": False},
            [{"$set": {"bindings": {"$concatArrays": [others, [bound]]}}}],
            session=self._mongodb_get_session(),
        )
        if not result.matched_count:
            raise AuthItemNotFoundError.for_uid(self.REGISTRY, binding.preset_uid)

    @t.override
    async def _unbind(self, preset_uid: int, attr_uid: int) -> None:
        collection = await self._mongodb_get_collection()
        result = await collection.update_one(
            {"_id": preset_uid, "deleted": False, "bindings.attr_uid": attr_uid},
            {"$pull": {"bindings": {"attr_uid": attr_uid}}},
            session=self._mongodb_get_session(),
        )
        if result.matched_count:
            return
        if await collection.count_documents(
            {"_id": preset_uid, "deleted": False}, session=self._mongodb_get_session()
        ):
            raise AuthItemNotFoundError.for_binding(self.REGISTRY, preset_uid, attr_uid)
        raise AuthItemNotFoundError.for_uid(self.REGISTRY, preset_uid)

    @t.override
    async def _get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        collection = await self._mongodb_get_collection()
        documents = collection.find(
            {"deleted": False}, {"bindings": True}, session=self._mongodb_get_session()
        ).sort("_id", 1)
        return tuple(
            [
                AuthSessionPresetBinding(
                    preset_uid=document["_id"],
                    attr_uid=bound["attr_uid"],
                    required=bound["required"],
                )
                async for document in documents
                for bound in sorted(document["bindings"], key=lambda b: b["attr_uid"])
            ]
        )
