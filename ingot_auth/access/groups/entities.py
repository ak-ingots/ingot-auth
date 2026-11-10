"""The groups: what each grants, declared in the code."""

__all__ = ("AuthGroup",)

import typing as t

from ingots.defaults.operations import Permissions
from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGroup(Entity):
    """
    A group of the users, a slot of :class:`AuthGroupsUnit`, its name the name
    of the slot. What it grants is of its hook, :meth:`_get_permissions`,
    nothing here: each class adds its own to ``super()``, so that an addon
    and the application grant to the same group, the application declaring
    the class that joins them.
    """

    project: "AuthProject"

    @t.final
    def get_name(self) -> str:
        """The name of the group: the path of its slot in the groups."""
        return self.project.auth.access.groups.slots_find_path(self)

    @t.final
    def get_permissions(self) -> Permissions:
        """What the group grants: the union of the hooks of its classes."""
        return self._get_permissions()

    def _get_permissions(self) -> Permissions:
        """What the class grants, with ``super()``: nothing here."""
        return Permissions()
