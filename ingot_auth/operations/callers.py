"""The callers of the defaults with the anonymous group of the auth."""

__all__ = ("AuthCallersProvider",)

import typing as t

from ingots.defaults.operations import CallersProvider, Permissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthCallersProvider(CallersProvider):
    """
    The callers of the project, the anonymous one given what the group
    ``grp_anonymous`` of the auth grants, what anyone may: a transport runs
    what is open to anyone for it, whatever a call bears. What an
    application grants anyone, or takes, it does in that group, as for
    ``grp_signed_in``.
    """

    project: "AuthProject"

    @t.override
    def _get_anonymous_permissions(self) -> Permissions:
        anonymous = self.project.auth.access.groups.grp_anonymous
        return super()._get_anonymous_permissions() | anonymous.get_permissions()
