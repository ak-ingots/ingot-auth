"""The strategy of the permissions of a user."""

__all__ = ("AuthGroupsGrants",)

import typing as t

from ingots.defaults.operations import Permissions
from ingots.puer import Entity

from .groups import AuthGroupNotFoundError

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGroupsGrants(Entity):
    """
    The permissions of a signed-in user: the union of what its groups grant,
    ``signed_in`` first, of every one. A membership of a group no source has
    any more grants nothing.
    """

    project: "AuthProject"

    @t.final
    async def get_permissions(self, uid: str) -> Permissions:
        """The permissions of the user of a uid, signed in."""
        groups = self.project.auth.access.groups
        permissions = groups.signed_in.get_permissions()
        for name in await self.project.auth.storage.access.members.get_groups(uid):
            try:
                group = groups.get(name)
            except AuthGroupNotFoundError:
                continue
            permissions |= group.get_permissions()
        return permissions
