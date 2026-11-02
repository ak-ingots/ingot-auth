"""The operations of the attributes of the sessions."""

__all__ = (
    "AuthCreateSessionAttr",
    "AuthDeleteSessionAttr",
    "AuthListSessionAttrs",
    "AuthRenameSessionAttr",
    "BaseAuthSessionAttrsOperation",
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

from .items import AuthSessionAttr
from .permissions import AuthSessionAttrsPermissions
from .storage import BaseAuthSessionAttrsStorage

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthSessionAttrsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthSessionAttr, ParametersType, ResultType]
):
    """An operation of the attributes of the sessions: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthSessionAttrsStorage:
        return self.project.auth.storage.session_attrs


class AuthCreateSessionAttr(
    BaseAuthCreateItem[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthSessionAttr, AuthSessionAttr],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_CREATE)


class AuthListSessionAttrs(
    BaseAuthListItems[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[None, tuple[AuthSessionAttr, ...]],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_READ)


class AuthRenameSessionAttr(
    BaseAuthRenameItem[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthRenameItemParameters, AuthSessionAttr],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_RENAME)


class AuthDeleteSessionAttr(
    BaseAuthDeleteItem[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthDeleteItemParameters, None],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_DELETE)
