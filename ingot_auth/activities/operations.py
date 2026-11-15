"""The operation of the read of the activity log."""

__all__ = ("AuthListActivitiesOperation",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.storages import AuthActivityQuery, AuthActivityRecord

from .items import AuthListActivitiesParameters

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

    from . import AuthActivitiesUnit


class AuthListActivitiesOperation(
    BaseOperation[AuthListActivitiesParameters, tuple[AuthActivityRecord, ...]]
):
    """The activities the parameters match, the newest first, as many as its limit."""

    project: "AuthProject"
    parent: "AuthActivitiesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_READ)

    @t.override
    async def _run(
        self, parameters: AuthListActivitiesParameters, metadata: OperationMetadata
    ) -> tuple[AuthActivityRecord, ...]:
        query: AuthActivityQuery = parameters
        return await self.project.auth.storage.activities.find(query)
