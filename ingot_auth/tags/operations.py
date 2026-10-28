"""The operations of the tags."""

__all__ = ("AuthCreateTag", "AuthDeleteTag", "AuthListTags", "AuthRenameTag")

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.permissions import AuthPermissions
from ingot_auth.registry.operations import (
    BaseAuthCreateItem,
    BaseAuthDeleteItem,
    BaseAuthListItems,
    BaseAuthRenameItem,
)

from .items import AuthTag
from .storage import BaseAuthTagsStorage

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthCreateTag(BaseAuthCreateItem[AuthTag]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.tags


class AuthListTags(BaseAuthListItems[AuthTag]):
    PERMISSIONS = Permissions(AuthPermissions.READ_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.tags


class AuthRenameTag(BaseAuthRenameItem[AuthTag]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.tags


class AuthDeleteTag(BaseAuthDeleteItem[AuthTag]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthTagsStorage:
        return self.project.auth.storage.tags
