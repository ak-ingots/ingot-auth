"""The storage of the presets of the sessions."""

__all__ = ("BaseAuthSessionPresetsStorage",)

import abc
import typing as t

from ..registry import BaseAuthRegistryStorage
from .items import AuthSessionPreset, AuthSessionPresetBinding


class BaseAuthSessionPresetsStorage(BaseAuthRegistryStorage[AuthSessionPreset]):
    """
    The storage of the presets of the sessions: what a backend implements.
    The bindings are of a preset: they go with it when it is deleted. An
    attribute is of another registry, so the storage does not look whether
    it is there; the operations do.
    """

    REGISTRY: t.ClassVar[str] = "sessions.presets"

    @t.final
    async def bind(self, binding: AuthSessionPresetBinding) -> None:
        """
        Binds an attribute to a preset, or tells anew whether the preset
        requires it.

        :raises AuthItemNotFoundError: no preset has the id.
        """
        await self._bind(binding)

    @t.final
    async def unbind(self, preset_id: int, attr_id: int) -> None:
        """
        Unbinds an attribute from a preset.

        :raises AuthItemNotFoundError: no preset has the id, or the attribute
            is not bound to it.
        """
        await self._unbind(preset_id, attr_id)

    @t.final
    async def get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        """The bindings of the presets, by the preset, then by the attribute."""
        return await self._get_bindings()

    @abc.abstractmethod
    async def _bind(self, binding: AuthSessionPresetBinding) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._bind")

    @abc.abstractmethod
    async def _unbind(self, preset_id: int, attr_id: int) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._unbind")

    @abc.abstractmethod
    async def _get_bindings(self) -> tuple[AuthSessionPresetBinding, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_bindings")
