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

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemorySessionPresetsStorage(
    AuthMemoryRegistryStorage[AuthSessionPreset], BaseAuthSessionPresetsStorage
):
    """The presets of the sessions in memory, each with its bindings."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        # the bindings by the preset: whether it requires each attribute
        self._bindings: dict[int, dict[int, bool]] = {}

    @t.override
    async def _delete(self, item_id: int) -> None:
        await super()._delete(item_id)
        self._bindings.pop(item_id, None)

    @t.override
    async def _bind(self, binding: AuthSessionPresetBinding) -> None:
        self._get(binding.preset_id)
        bindings = self._bindings.setdefault(binding.preset_id, {})
        bindings[binding.attr_id] = binding.required

    @t.override
    async def _unbind(self, preset_id: int, attr_id: int) -> None:
        self._get(preset_id)
        try:
            del self._bindings.get(preset_id, {})[attr_id]
        except KeyError:
            raise AuthItemNotFoundError.for_binding(
                self.REGISTRY, preset_id, attr_id
            ) from None

    @t.override
    async def _get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        return tuple(
            AuthSessionPresetBinding(
                preset_id=preset_id, attr_id=attr_id, required=required
            )
            for preset_id in sorted(self._bindings)
            for attr_id, required in sorted(self._bindings[preset_id].items())
        )
