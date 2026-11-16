"""The callers of the defaults with the anonymous group of the auth."""

__all__ = ("AuthCallersProvider",)

import typing as t

from ingots.defaults.operations import Caller, CallersProvider, Permissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthCallersProvider(CallersProvider):
    """
    The callers of the project, the anonymous one given what the group
    ``auth.grp_anonymous`` grants, what anyone may: a transport runs what is
    open to anyone for it, whatever a call bears. What an application grants
    anyone, or takes, it does by its class in the slot of that group, as for
    ``auth.grp_signed_in``. The server acting by itself is the caller
    ``auth.system``, :meth:`get_auth_system`, given what ``auth.grp_system``
    grants.
    """

    project: "AuthProject"

    @t.final
    def get_auth_system(self) -> Caller:
        """
        The caller of what the server does by itself, a session expiring, a
        job of a schedule: not the initiative of a user, nor of an operator.
        """
        permissions = self.project.auth.grp_system.get_permissions()
        return Caller(uid="auth.system", permissions=permissions)

    @t.override
    def _get_anonymous_permissions(self) -> Permissions:
        anonymous = self.project.auth.grp_anonymous
        return super()._get_anonymous_permissions() | anonymous.get_permissions()
