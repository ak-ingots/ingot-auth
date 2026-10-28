"""The operations of the attributes."""

__all__ = ("AuthCreateAttr", "AuthDeleteAttr", "AuthListAttrs", "AuthRenameAttr")

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.permissions import AuthPermissions
from ingot_auth.registry.operations import (
    BaseAuthCreateItem,
    BaseAuthDeleteItem,
    BaseAuthListItems,
    BaseAuthRenameItem,
)

from .items import AuthAttr
from .storage import BaseAuthAttrsStorage

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthCreateAttr(BaseAuthCreateItem[AuthAttr]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.attrs


class AuthListAttrs(BaseAuthListItems[AuthAttr]):
    PERMISSIONS = Permissions(AuthPermissions.READ_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.attrs


class AuthRenameAttr(BaseAuthRenameItem[AuthAttr]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.attrs


class AuthDeleteAttr(BaseAuthDeleteItem[AuthAttr]):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.attrs
