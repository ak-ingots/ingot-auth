"""The operations of the groups."""

__all__ = ("AuthListGroupsOperation",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from .items import AuthGroupInfo

if t.TYPE_CHECKING:
    from . import AuthGroupsUnit
    from ingot_auth.project import AuthProject


class AuthListGroupsOperation(BaseOperation[None, tuple[AuthGroupInfo, ...]]):
    """The groups, in the order of their slots, each with what it grants."""

    project: "AuthProject"
    parent: "AuthGroupsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[AuthGroupInfo, ...]:
        return tuple(
            AuthGroupInfo(name=group.get_name(), permissions=group.get_permissions())
            for group in self.project.auth.access.groups.get_all()
        )
