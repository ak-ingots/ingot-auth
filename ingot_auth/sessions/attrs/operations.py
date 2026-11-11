"""The operations of the attributes of the sessions."""

__all__ = (
    "AuthCreateSessionAttrOperation",
    "AuthDeleteSessionAttrOperation",
    "AuthListSessionAttrsOperation",
    "AuthRenameSessionAttrOperation",
    "BaseAuthSessionAttrsOperation",
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
from ingot_auth.storages import AuthSessionAttr, BaseAuthSessionAttrsStorage

from .permissions import AuthSessionAttrsPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthSessionAttrsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthSessionAttr, ParametersType, ResultType]
):
    """An operation of the attributes of the sessions: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthSessionAttrsStorage:
        return self.project.auth.storage.sessions.attrs


class AuthCreateSessionAttrOperation(
    BaseAuthCreateItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthSessionAttr, AuthSessionAttr],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_CREATE)


class AuthListSessionAttrsOperation(
    BaseAuthListItemsOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[None, tuple[AuthSessionAttr, ...]],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_READ)


class AuthRenameSessionAttrOperation(
    BaseAuthRenameItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthRenameItemParameters, AuthSessionAttr],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_RENAME)


class AuthDeleteSessionAttrOperation(
    BaseAuthDeleteItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthDeleteItemParameters, None],
):
    PERMISSIONS = Permissions(AuthSessionAttrsPermissions.CAN_DELETE)
