"""The operations of the attributes."""

__all__ = (
    "AuthCreateAttr",
    "AuthDeleteAttr",
    "AuthListAttrs",
    "AuthRenameAttr",
    "BaseAuthAttrsOperation",
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

from .items import AuthAttr
from .storage import BaseAuthAttrsStorage

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthAttrsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthAttr, ParametersType, ResultType]
):
    """An operation of the attributes: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.attrs


class AuthCreateAttr(
    BaseAuthCreateItem[AuthAttr], BaseAuthAttrsOperation[AuthAttr, AuthAttr]
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)


class AuthListAttrs(
    BaseAuthListItems[AuthAttr],
    BaseAuthAttrsOperation[None, tuple[AuthAttr, ...]],
):
    PERMISSIONS = Permissions(AuthPermissions.READ_REGISTRY)


class AuthRenameAttr(
    BaseAuthRenameItem[AuthAttr],
    BaseAuthAttrsOperation[AuthRenameItemParameters, AuthAttr],
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)


class AuthDeleteAttr(
    BaseAuthDeleteItem[AuthAttr],
    BaseAuthAttrsOperation[AuthDeleteItemParameters, None],
):
    PERMISSIONS = Permissions(AuthPermissions.MANAGE_REGISTRY)
