"""The groups of the profiles: who reads their registries, who keeps them."""

__all__ = ("AuthProfilesConsumersGroup", "AuthProfilesManagersGroup")

import typing as t

from ingots.defaults.operations import Permissions

from ingot_auth.access.groups import AuthGroup

if t.TYPE_CHECKING:
    from . import AuthProfilesUnit


class AuthProfilesConsumersGroup(AuthGroup):
    """Who reads the registries of the profiles, the tags and the attributes."""

    parent: "AuthProfilesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        tags = self.parent.tags.permissions
        attrs = self.parent.attrs.permissions
        return (
            super()._get_permissions()
            | tags(tags.flags.CAN_READ)
            | attrs(attrs.flags.CAN_READ)
        )


class AuthProfilesManagersGroup(AuthGroup):
    """
    Who keeps the registries of the profiles, the tags and the attributes:
    creates, reads, updates and deletes their items.
    """

    parent: "AuthProfilesUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        tags = self.parent.tags.permissions
        attrs = self.parent.attrs.permissions
        return (
            super()._get_permissions()
            | tags(
                tags.flags.CAN_CREATE,
                tags.flags.CAN_READ,
                tags.flags.CAN_UPDATE,
                tags.flags.CAN_DELETE,
            )
            | attrs(
                attrs.flags.CAN_CREATE,
                attrs.flags.CAN_READ,
                attrs.flags.CAN_UPDATE,
                attrs.flags.CAN_DELETE,
            )
        )
