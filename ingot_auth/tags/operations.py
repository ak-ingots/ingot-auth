"""The operations of the tags."""

__all__ = (
    "AuthCreateTag",
    "AuthDeleteTag",
    "AuthListTags",
    "AuthRenameTag",
    "BaseAuthTagsOperation",
)

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.permissions import AuthPermissions
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
    BaseAuthCreateItem,
    BaseAuthDeleteItem,
    BaseAuthListItems,
    BaseAuthRegistryOperation,
    BaseAuthRenameItem,
)

from .items import AuthTag
from .storage import BaseAuthTagsStorage

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthTagsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthTag, ParametersType, ResultType]
):
    """An operation of the tags: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.tags


class AuthCreateTag(
    BaseAuthCreateItem[AuthTag], BaseAuthTagsOperation[AuthTag, AuthTag]
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)


class AuthListTags(
    BaseAuthListItems[AuthTag],
    BaseAuthTagsOperation[None, tuple[AuthTag, ...]],
):
    PERMISSIONS = Permissions(AuthPermissions.READ_REGISTRY)


class AuthRenameTag(
    BaseAuthRenameItem[AuthTag],
    BaseAuthTagsOperation[AuthRenameItemParameters, AuthTag],
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)


class AuthDeleteTag(
    BaseAuthDeleteItem[AuthTag],
    BaseAuthTagsOperation[AuthDeleteItemParameters, None],
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
