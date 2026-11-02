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
from .permissions import AuthAttrsPermissions
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
        return self.project.auth.storage.profile.attrs


class AuthCreateAttr(
    BaseAuthCreateItem[AuthAttr], BaseAuthAttrsOperation[AuthAttr, AuthAttr]
):
    PERMISSIONS = Permissions(AuthAttrsPermissions.CAN_CREATE)


class AuthListAttrs(
    BaseAuthListItems[AuthAttr],
    BaseAuthAttrsOperation[None, tuple[AuthAttr, ...]],
):
    PERMISSIONS = Permissions(AuthAttrsPermissions.CAN_READ)


class AuthRenameAttr(
    BaseAuthRenameItem[AuthAttr],
    BaseAuthAttrsOperation[AuthRenameItemParameters, AuthAttr],
):
    PERMISSIONS = Permissions(AuthAttrsPermissions.CAN_UPDATE)


class AuthDeleteAttr(
    BaseAuthDeleteItem[AuthAttr],
    BaseAuthAttrsOperation[AuthDeleteItemParameters, None],
):
    PERMISSIONS = Permissions(AuthAttrsPermissions.CAN_DELETE)
