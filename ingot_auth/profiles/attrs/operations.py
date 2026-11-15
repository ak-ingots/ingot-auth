"""The operations of the attributes."""

__all__ = (
    "AuthCreateAttrOperation",
    "AuthDeleteAttrOperation",
    "AuthListAttrsOperation",
    "AuthRenameAttrOperation",
    "BaseAuthAttrsOperation",
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
from ingot_auth.storages import AuthAttr, BaseAuthAttrsStorage

if t.TYPE_CHECKING:
    from . import AuthAttrsUnit
    from ingot_auth.project import AuthProject


class BaseAuthAttrsOperation[ParametersType, ResultType](
    BaseAuthRegistryOperation[AuthAttr, ParametersType, ResultType]
):
    """An operation of the attributes: works with their storage."""

    project: "AuthProject"

    @t.override
    def _get_storage(self) -> BaseAuthAttrsStorage:
        return self.project.auth.storage.profiles.attrs


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttrCreated(AuthActivityContext):
    """The context of an attribute created in the activity log."""

    name: str
    type: str


class AuthCreateAttrOperation(
    BaseAuthCreateItemOperation[AuthAttr], BaseAuthAttrsOperation[AuthAttr, AuthAttr]
):
    parent: "AuthAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_CREATE)

    @t.override
    def _get_created_context(self, item: AuthAttr) -> AuthAttrCreated:
        return AuthAttrCreated(name=item.name, type=item.type.value)


class AuthListAttrsOperation(
    BaseAuthListItemsOperation[AuthAttr],
    BaseAuthAttrsOperation[None, tuple[AuthAttr, ...]],
):
    parent: "AuthAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)


class AuthRenameAttrOperation(
    BaseAuthRenameItemOperation[AuthAttr],
    BaseAuthAttrsOperation[AuthRenameItemParameters, AuthAttr],
):
    parent: "AuthAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_UPDATE)


class AuthDeleteAttrOperation(
    BaseAuthDeleteItemOperation[AuthAttr],
    BaseAuthAttrsOperation[AuthDeleteItemParameters, None],
):
    parent: "AuthAttrsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_DELETE)
