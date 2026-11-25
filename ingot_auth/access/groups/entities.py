"""The groups: what each grants, declared in the code."""

__all__ = ("AuthAnonymousGroup", "AuthGroup", "AuthSignedInGroup", "AuthSystemGroup")

import typing as t

from ingots.defaults.operations import Permissions
from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGroup(Entity):
    """
    A group of the users, in a slot of a unit of its domain, an
    :class:`~.AuthGroupsOwner`, the slot prefixed ``grp_``: its name is its
    full name, where it is, ``shop.grp_buyers``, the scripts and the
    memberships naming it. What a group grants is of its hook,
    :meth:`_get_permissions`, nothing here: each class adds its own to
    ``super()``, so that an addon and the application grant to the same
    group, the application declaring the class that joins them; a class in
    no slot is a mixin of what it grants, for a group an application
    declares.
    """

    project: "AuthProject"

    @t.final
    def get_name(self) -> str:
        """The name of the group, its full name."""
        return self.full_name

    @t.final
    def get_permissions(self) -> Permissions:
        """What the group grants: the union of the hooks of its classes."""
        return self._get_permissions()

    def _get_permissions(self) -> Permissions:
        """What the class grants, with ``super()``: nothing here."""
        return Permissions()


class AuthSignedInGroup(AuthGroup):
    """
    The group of every signed-in user, of the core, a member none stored,
    in the slot ``grp_signed_in`` of the auth. It grants what the methods
    give a signed-in user by their toggles, the ``CAN_SIGN_IN`` of each
    method open, the listing and the revoking of its own sessions, the
    reading of its own profile and the change of its own password; what
    an application and its addons grant every signed-in
    user, they add by the hook, the application declaring the class that
    joins them in the slot.
    """

    @t.override
    def _get_permissions(self) -> Permissions:
        auth = self.project.auth
        sessions = auth.sessions.permissions
        profiles = auth.profiles.permissions
        password = auth.methods.password.permissions
        return (
            super()._get_permissions()
            | auth.methods.get_signed_in_permissions()
            | sessions(sessions.flags.CAN_LIST_OWN, sessions.flags.CAN_REVOKE_OWN)
            | profiles(profiles.flags.CAN_READ_OWN)
            | password(password.flags.CAN_CHANGE)
        )


class AuthAnonymousGroup(AuthGroup):
    """
    The group of every caller that tells no one, of the core, a member none
    stored, in the slot ``grp_anonymous`` of the auth: the anonymous caller
    of the project has what it grants. It grants what anyone may of the
    auth, as its units tell it: the flags of the sign-up and of the
    sign-in, those of the methods their toggles open, the reading of the
    metadata; what an application and its addons grant anyone, they add by
    the hook, or take, the metadata closed for one, the application
    declaring the class that joins them in the slot. A signed-in user is not
    a member: it has what its groups grant.
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


class AuthSystemGroup(AuthGroup):
    """
    The group of the server acting by itself, of the core, a member none
    stored, in the slot ``grp_system`` of the auth: the caller ``auth.system``
    of the project has what it grants, a job of a schedule running as it. It
    grants the sweep of the expired sessions; what an application gives a
    job of its own, it adds by the hook, the application declaring the class
    that joins them in the slot.
    """

    @t.override
    def _get_permissions(self) -> Permissions:
        sessions = self.project.auth.sessions.permissions
        return super()._get_permissions() | sessions(sessions.flags.CAN_SWEEP)
