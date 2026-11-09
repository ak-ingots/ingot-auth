"""The operations of the groups."""

__all__ = ("AuthListGroups",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from .items import AuthGroupInfo
from .permissions import AuthGroupsPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthListGroups(BaseOperation[None, tuple[AuthGroupInfo, ...]]):
    """The groups, in the order of their slots, each with what it grants."""

    PERMISSIONS = Permissions(AuthGroupsPermissions.CAN_READ)

    project: "AuthProject"

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[AuthGroupInfo, ...]:
        return tuple(
            AuthGroupInfo(name=group.get_name(), permissions=group.get_permissions())
            for group in self.project.auth.access.groups.get_all()
        )
