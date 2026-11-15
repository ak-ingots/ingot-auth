"""The operations of the attributes of the sessions."""

__all__ = (
    "AuthCreateSessionAttrOperation",
    "AuthDeleteSessionAttrOperation",
    "AuthListSessionAttrsOperation",
    "AuthRenameSessionAttrOperation",
    "BaseAuthSessionAttrsOperation",
)

import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import Permissions

from ingot_auth.activities import AuthActivityContext

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

if t.TYPE_CHECKING:
    from . import AuthSessionAttrsUnit
    from ingot_auth.project import AuthProject


class BaseAuthSessionAttrsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthSessionAttr, ParametersType, ResultType]
):
    """An operation of the attributes of the sessions: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthSessionAttrsStorage:
        return self.project.auth.storage.sessions.attrs


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionAttrCreated(AuthActivityContext):
    """The context of an attribute of the sessions created in the activity log."""

    name: str
    type: str
    source: str


class AuthCreateSessionAttrOperation(
    BaseAuthCreateItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthSessionAttr, AuthSessionAttr],
):
    parent: "AuthSessionAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_CREATE)

    @t.override
    def _get_created_context(self, item: AuthSessionAttr) -> AuthSessionAttrCreated:
        return AuthSessionAttrCreated(
            name=item.name, type=item.type.value, source=item.source.value
        )


class AuthListSessionAttrsOperation(
    BaseAuthListItemsOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[None, tuple[AuthSessionAttr, ...]],
):
    parent: "AuthSessionAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)


class AuthRenameSessionAttrOperation(
    BaseAuthRenameItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthRenameItemParameters, AuthSessionAttr],
):
    parent: "AuthSessionAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_RENAME)


class AuthDeleteSessionAttrOperation(
    BaseAuthDeleteItemOperation[AuthSessionAttr],
    BaseAuthSessionAttrsOperation[AuthDeleteItemParameters, None],
):
    parent: "AuthSessionAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_DELETE)
