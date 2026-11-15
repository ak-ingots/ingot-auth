"""The presets of the sessions in memory."""

__all__ = ("AuthMemorySessionPresetsStorage",)

import typing as t

from ingot_auth.storages import (
    AuthItemNotFoundError,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    BaseAuthSessionPresetsStorage,
)

from ..registry import AuthMemoryRegistryStorage


class AuthMemorySessionPresetsStorage(
    AuthMemoryRegistryStorage[AuthSessionPreset], BaseAuthSessionPresetsStorage
):
    """The presets of the sessions in memory, each with its bindings."""

    def __init__(self) -> None:
        super().__init__()
        # the bindings by the preset: whether it requires each attribute
        self._bindings: dict[int, dict[int, bool]] = {}

    @t.override
    async def _delete(self, item_uid: int) -> None:
        await super()._delete(item_uid)
        self._bindings.pop(item_uid, None)

    @t.override
    async def _bind(self, binding: AuthSessionPresetBinding) -> None:
        self._get(binding.preset_uid)
        bindings = self._bindings.setdefault(binding.preset_uid, {})
        bindings[binding.attr_uid] = binding.required

    @t.override
    async def _unbind(self, preset_uid: int, attr_uid: int) -> None:
        self._get(preset_uid)
        try:
            del self._bindings.get(preset_uid, {})[attr_uid]
        except KeyError:
            raise AuthItemNotFoundError.for_binding(
                self.REGISTRY, preset_uid, attr_uid
            ) from None

    @t.override
    async def _get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        return tuple(
            AuthSessionPresetBinding(
                preset_uid=preset_uid, attr_uid=attr_uid, required=required
            )
            for preset_uid in sorted(self._bindings)
            for attr_uid, required in sorted(self._bindings[preset_uid].items())
        )
