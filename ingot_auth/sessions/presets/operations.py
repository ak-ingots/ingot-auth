"""The operations of the presets of the sessions."""

__all__ = (
    "AuthBindSessionAttrOperation",
    "AuthCreateSessionPresetOperation",
    "AuthDeleteSessionPresetOperation",
    "AuthListSessionPresetBindingsOperation",
    "AuthListSessionPresetsOperation",
    "AuthRenameSessionPresetOperation",
    "AuthUnbindSessionAttrParameters",
    "AuthUnbindSessionAttrOperation",
    "BaseAuthSessionPresetsOperation",
)

import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import OperationMetadata, Permissions

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
    BaseAuthCreateItemOperation,
    BaseAuthDeleteItemOperation,
    BaseAuthListItemsOperation,
    BaseAuthRegistryOperation,
    BaseAuthRenameItemOperation,
)
from ingot_auth.storages import (
    AuthItemNotFoundError,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    BaseAuthSessionPresetsStorage,
)

if t.TYPE_CHECKING:
    from . import AuthSessionPresetsUnit
    from ingot_auth.project import AuthProject


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthUnbindSessionAttrParameters:
    preset_id: int
    attr_id: int


class BaseAuthSessionPresetsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthSessionPreset, ParametersType, ResultType]
):
    """An operation of the presets of the sessions: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthSessionPresetsStorage:
        return self.project.auth.storage.sessions.presets

    async def _get_attr_ids(self) -> set[int]:
        """The ids of the attributes of the sessions there are."""
        attrs = await self.project.auth.storage.sessions.attrs.get_all()
        return {attr.id for attr in attrs}


class AuthCreateSessionPresetOperation(
    BaseAuthCreateItemOperation[AuthSessionPreset],
    BaseAuthSessionPresetsOperation[AuthSessionPreset, AuthSessionPreset],
):
    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_CREATE)


class AuthListSessionPresetsOperation(
    BaseAuthListItemsOperation[AuthSessionPreset],
    BaseAuthSessionPresetsOperation[None, tuple[AuthSessionPreset, ...]],
):
    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)


class AuthRenameSessionPresetOperation(
    BaseAuthRenameItemOperation[AuthSessionPreset],
    BaseAuthSessionPresetsOperation[AuthRenameItemParameters, AuthSessionPreset],
):
    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_RENAME)


class AuthDeleteSessionPresetOperation(
    BaseAuthDeleteItemOperation[AuthSessionPreset],
    BaseAuthSessionPresetsOperation[AuthDeleteItemParameters, None],
):
    """Deletes a preset with its bindings; its id is never given again."""

    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_DELETE)


class AuthBindSessionAttrOperation(
    BaseAuthSessionPresetsOperation[AuthSessionPresetBinding, AuthSessionPresetBinding]
):
    """
    Binds an attribute of the sessions to a preset, or tells anew whether the
    preset requires it, returning the binding.
    """

    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_BIND)

    @t.override
    async def _run(
        self, parameters: AuthSessionPresetBinding, metadata: OperationMetadata
    ) -> AuthSessionPresetBinding:
        if parameters.attr_id not in await self._get_attr_ids():
            registry = self.project.auth.storage.sessions.attrs.REGISTRY
            raise AuthItemNotFoundError.for_id(registry, parameters.attr_id)
        await self._get_storage().bind(parameters)
        return parameters


class AuthUnbindSessionAttrOperation(
    BaseAuthSessionPresetsOperation[AuthUnbindSessionAttrParameters, None]
):
    """Unbinds an attribute of the sessions from a preset."""

    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_UNBIND)

    @t.override
    async def _run(
        self, parameters: AuthUnbindSessionAttrParameters, metadata: OperationMetadata
    ) -> None:
        await self._get_storage().unbind(parameters.preset_id, parameters.attr_id)


class AuthListSessionPresetBindingsOperation(
    BaseAuthSessionPresetsOperation[None, tuple[AuthSessionPresetBinding, ...]]
):
    """
    The bindings of the presets, by the preset, then by the attribute. A
    deleted attribute is not in them: it is gone from the presets with it.
    """

    parent: "AuthSessionPresetsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[AuthSessionPresetBinding, ...]:
        attr_ids = await self._get_attr_ids()
        bindings = await self._get_storage().get_bindings()
        return tuple(binding for binding in bindings if binding.attr_id in attr_ids)
