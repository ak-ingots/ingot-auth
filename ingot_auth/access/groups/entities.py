"""The groups: what each grants, declared in the code."""

__all__ = ("AuthAnonymousGroup", "AuthGroup", "AuthSignedInGroup")

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


class AuthSignedInGroup(AuthGroup):
    """
    The group ``grp_signed_in`` of the core: every signed-in user is a member,
    none stored. It grants what the methods give a signed-in user by their
    toggles, the ``CAN_SIGN_IN`` of each method open; what an application
    and its addons grant every signed-in user, they add by the hook, the
    application declaring the class that joins them in the slot.
    """

    @t.override
    def _get_permissions(self) -> Permissions:
        methods = self.project.auth.methods
        return super()._get_permissions() | methods.get_signed_in_permissions()


class AuthAnonymousGroup(AuthGroup):
    """
    The group ``grp_anonymous`` of the core: every caller that tells no one
    is a member, none stored, the anonymous caller of the project having
    what it grants. It grants what anyone may of the auth, as its units tell it: the
    flags of the sign-up and of the sign-in, those of the methods their
    toggles open, the reading of the metadata; what an application and its
    addons grant anyone, they add by the hook, or take, the metadata closed
    for one, the application declaring the class that joins them in the
    slot. A signed-in user is not a member: it has what its groups grant.
    """

    @t.override
    def _get_permissions(self) -> Permissions:
        auth = self.project.auth
        return (
            super()._get_permissions()
            | auth.sign_up.get_anonymous_permissions()
            | auth.sign_in.get_anonymous_permissions()
            | auth.methods.get_anonymous_permissions()
            | auth.metadata.get_anonymous_permissions()
        )
