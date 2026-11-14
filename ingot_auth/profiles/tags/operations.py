"""The operations of the tags."""

__all__ = (
    "AuthCreateTagOperation",
    "AuthDeleteTagOperation",
    "AuthListTagsOperation",
    "AuthRenameTagOperation",
    "BaseAuthTagsOperation",
)

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
    BaseAuthCreateItemOperation,
    BaseAuthDeleteItemOperation,
    BaseAuthListItemsOperation,
    BaseAuthRegistryOperation,
    BaseAuthRenameItemOperation,
)
from ingot_auth.storages import AuthTag, BaseAuthTagsStorage

if t.TYPE_CHECKING:
    from . import AuthTagsUnit
    from ingot_auth.project import AuthProject


class BaseAuthTagsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthTag, ParametersType, ResultType]
):
    """An operation of the tags: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.profiles.tags


class AuthCreateTagOperation(
    BaseAuthCreateItemOperation[AuthTag], BaseAuthTagsOperation[AuthTag, AuthTag]
):
    parent: "AuthTagsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_CREATE)


class AuthListTagsOperation(
    BaseAuthListItemsOperation[AuthTag],
    BaseAuthTagsOperation[None, tuple[AuthTag, ...]],
):
    parent: "AuthTagsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)


class AuthRenameTagOperation(
    BaseAuthRenameItemOperation[AuthTag],
    BaseAuthTagsOperation[AuthRenameItemParameters, AuthTag],
):
    parent: "AuthTagsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_UPDATE)


class AuthDeleteTagOperation(
    BaseAuthDeleteItemOperation[AuthTag],
    BaseAuthTagsOperation[AuthDeleteItemParameters, None],
):
    parent: "AuthTagsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_DELETE)
