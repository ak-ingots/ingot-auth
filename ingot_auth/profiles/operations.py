"""The operations of the values of the profiles."""

__all__ = ("AuthSetProfileAttrValuesOperation", "AuthSetProfileTagsOperation")

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import (
    ATTR_VALUE_TYPES,
    AuthItemNotFoundError,
    AuthProfileValues,
)

from .items import AuthSetProfileAttrValuesParameters, AuthSetProfileTagsParameters

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

    from . import AuthProfilesUnit


class AuthSetProfileTagsOperation(
    BaseOperation[AuthSetProfileTagsParameters, AuthProfileValues]
):
    """
    Sets the tags of a profile, all of them, in place of those it had, and
    gives its values; its callers are forgotten, so that the next request of
    each tells what changed. Run twice, it changes nothing more.

    :raises AuthProfileNotFoundError: no profile has the uid.
    :raises AuthItemNotFoundError: no tag of the registry has an id.
    """

    project: "AuthProject"
    parent: "AuthProfilesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_UPDATE)

    @t.override
    async def _run(
        self, parameters: AuthSetProfileTagsParameters, metadata: OperationMetadata
    ) -> AuthProfileValues:
        storage = self.project.auth.storage.profiles
        await storage.get(parameters.uid)
        known = {tag.id for tag in await storage.tags.get_all()}
        if unknown := sorted(parameters.tag_ids - known):
            raise AuthItemNotFoundError.for_id(storage.tags.REGISTRY, unknown[0])
        await storage.values.set_tags(parameters.uid, parameters.tag_ids)
        await self.project.auth.sessions.forget_callers(parameters.uid)
        return await storage.values.get(parameters.uid)


class AuthSetProfileAttrValuesOperation(
    BaseOperation[AuthSetProfileAttrValuesParameters, AuthProfileValues]
):
    """
    Sets the values of the attributes of a profile, all of them, in place of
    those it had, and gives its values; its callers are forgotten.

    :raises AuthProfileNotFoundError: no profile has the uid.
    :raises AuthItemNotFoundError: no attribute of the registry has an id.
    :raises AuthItemInvalidError: a value is not of the type of its attribute.
    """

    project: "AuthProject"
    parent: "AuthProfilesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_UPDATE)

    @t.override
    async def _run(
        self,
        parameters: AuthSetProfileAttrValuesParameters,
        metadata: OperationMetadata,
    ) -> AuthProfileValues:
        storage = self.project.auth.storage.profiles
        await storage.get(parameters.uid)
        registry = storage.attrs.REGISTRY
        attrs = {attr.id: attr for attr in await storage.attrs.get_all()}
        for attr_id, value in parameters.attr_values.items():
            try:
                attr = attrs[attr_id]
            except KeyError:
                raise AuthItemNotFoundError.for_id(registry, attr_id) from None
            if type(value) is not ATTR_VALUE_TYPES[attr.type]:
                raise AuthItemInvalidError.for_value(registry, attr_id)
        await storage.values.set_attr_values(parameters.uid, parameters.attr_values)
        await self.project.auth.sessions.forget_callers(parameters.uid)
        return await storage.values.get(parameters.uid)
