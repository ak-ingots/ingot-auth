"""
The groups of the sessions: who reads their registries, who keeps them, who
binds the attributes to the presets too.
"""

__all__ = (
    "AuthSessionsAdminsGroup",
    "AuthSessionsConsumersGroup",
    "AuthSessionsManagersGroup",
)

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.access.groups import AuthGroup

if t.TYPE_CHECKING:
    from . import AuthSessionsUnit


class AuthSessionsConsumersGroup(AuthGroup):
    """Who reads the registries of the sessions, the attributes and the presets."""

    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        attrs = self.parent.attrs.permissions
        presets = self.parent.presets.permissions
        return (
            super()._get_permissions()
            | attrs(attrs.flags.CAN_READ)
            | presets(presets.flags.CAN_READ)
        )


class AuthSessionsManagersGroup(AuthGroup):
    """
    Who keeps the registries of the sessions, the attributes and the
    presets: creates, reads, renames and deletes their items, binding none.
    """

    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        attrs = self.parent.attrs.permissions
        presets = self.parent.presets.permissions
        return (
            super()._get_permissions()
            | attrs(
                attrs.flags.CAN_CREATE,
                attrs.flags.CAN_READ,
                attrs.flags.CAN_RENAME,
                attrs.flags.CAN_DELETE,
            )
            | presets(
                presets.flags.CAN_CREATE,
                presets.flags.CAN_READ,
                presets.flags.CAN_RENAME,
                presets.flags.CAN_DELETE,
            )
        )


class AuthSessionsAdminsGroup(AuthGroup):
    """
    Who keeps the registries of the sessions and binds the attributes to the
    presets: all a manager does, and the bindings; who reads the record of
    the sign-ins of a profile too, and who revokes its sessions.
    """

    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        sessions = self.parent.permissions
        attrs = self.parent.attrs.permissions
        presets = self.parent.presets.permissions
        return (
            super()._get_permissions()
            | sessions(sessions.flags.CAN_LIST, sessions.flags.CAN_REVOKE)
            | attrs(
                attrs.flags.CAN_CREATE,
                attrs.flags.CAN_READ,
                attrs.flags.CAN_RENAME,
                attrs.flags.CAN_DELETE,
            )
            | presets(
                presets.flags.CAN_CREATE,
                presets.flags.CAN_READ,
                presets.flags.CAN_RENAME,
                presets.flags.CAN_DELETE,
                presets.flags.CAN_BIND,
                presets.flags.CAN_UNBIND,
            )
        )
