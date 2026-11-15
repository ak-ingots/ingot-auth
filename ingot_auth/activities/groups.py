"""The group of the auditors, who read the activity log."""

__all__ = ("AuthActivitiesAuditorsGroup",)

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.access.groups import AuthGroup

if t.TYPE_CHECKING:
    from . import AuthActivitiesUnit


class AuthActivitiesAuditorsGroup(AuthGroup):
    """Who reads the activity log, every change of state of the auth."""

    parent: "AuthActivitiesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return super()._get_permissions() | permissions(permissions.flags.CAN_READ)
