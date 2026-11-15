"""The operations of the values of the profiles."""

__all__ = (
    "AuthGetOwnProfileOperation",
    "AuthSetProfileAttrValuesOperation",
    "AuthSetProfileTagsOperation",
)

import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.activities import AuthActivityContext
from ingot_auth.caches import AuthCaller
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import (
    ATTR_VALUE_TYPES,
    AuthActivityAction,
    AuthItemNotFoundError,
    AuthProfileNotFoundError,
    AuthProfileValues,
)

from .items import (
    AuthOwnProfile,
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsParameters,
)

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue

    from . import AuthProfilesUnit


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfileTagsSet(AuthActivityContext):
    """The context of the tags of a profile set: the ids of them all."""

    tag_uids: frozenset[int]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfileAttrValuesSet(AuthActivityContext):
    """The context of the values of a profile set: all, by the ids of the attributes."""

    attr_values: "dict[int, AuthAttrValue]"


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
        known = {tag.uid for tag in await storage.tags.get_all()}
        if unknown := sorted(parameters.tag_uids - known):
            raise AuthItemNotFoundError.for_uid(storage.tags.REGISTRY, unknown[0])
        auth = self.project.auth
        async with auth.storage.transaction():
            await storage.values.set_tags(parameters.uid, parameters.tag_uids)
            await auth.activities.record(
                self.parent,
                parameters.uid,
                AuthActivityAction.UPDATE,
                metadata,
                context=AuthProfileTagsSet(tag_uids=parameters.tag_uids),
            )
        await auth.sessions.forget_callers(parameters.uid)
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
        attrs = {attr.uid: attr for attr in await storage.attrs.get_all()}
        for attr_uid, value in parameters.attr_values.items():
            try:
                attr = attrs[attr_uid]
            except KeyError:
                raise AuthItemNotFoundError.for_uid(registry, attr_uid) from None
            if type(value) is not ATTR_VALUE_TYPES[attr.type]:
                raise AuthItemInvalidError.for_value(registry, attr_uid)
        auth = self.project.auth
        async with auth.storage.transaction():
            await storage.values.set_attr_values(parameters.uid, parameters.attr_values)
            await auth.activities.record(
                self.parent,
                parameters.uid,
                AuthActivityAction.UPDATE,
                metadata,
                context=AuthProfileAttrValuesSet(
                    attr_values=dict(parameters.attr_values)
                ),
            )
        await auth.sessions.forget_callers(parameters.uid)
        return await storage.values.get(parameters.uid)


class AuthGetOwnProfileOperation(BaseOperation[None, AuthOwnProfile]):
    """
    The profile of the caller, its values, its permissions and the hash its
    replies tell.

    :raises AuthProfileNotFoundError: the caller has no profile, the root.
    """

    project: "AuthProject"
    parent: "AuthProfilesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ_OWN)

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> AuthOwnProfile:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            raise AuthProfileNotFoundError.for_uid(caller.uid)
        values = await self.project.auth.storage.profiles.values.get(caller.uid)
        return AuthOwnProfile(
            tag_uids=values.tag_uids,
            attr_values=values.attr_values,
            permissions=dict(caller.permissions),
            hash=caller.profile_hash,
        )
