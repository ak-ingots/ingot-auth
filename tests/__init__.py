"""
The test suite, with the callers it runs as and the masks it expects: a flag
tells no domain since ingots 0.34, so :func:`masks` puts each in that of its
unit in the projects of the tests, ``auth.sign_up`` for the sign-up.
"""

import typing as t
from collections.abc import Mapping

from ingots.defaults.operations import (
    Caller,
    CallersProvider,
    PermissionFlags,
    Permissions,
)

from ingot_auth.access.groups import AuthGroupsPermissions
from ingot_auth.access.members import AuthMembersPermissions
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.methods.email_code import AuthEmailCodePermissions
from ingot_auth.methods.nickname import AuthNicknamePermissions
from ingot_auth.profiles.attrs import AuthAttrsPermissions
from ingot_auth.profiles.tags import AuthTagsPermissions
from ingot_auth.sessions.attrs import AuthSessionAttrsPermissions
from ingot_auth.sessions.presets import AuthSessionPresetsPermissions
from ingot_auth.sign_in import AuthSignInPermissions
from ingot_auth.sign_up import AuthSignUpPermissions
from ingot_auth.testing.methods import AuthTestingPermissions

ROOT: t.Final = CallersProvider.ROOT
ANONYMOUS: t.Final = Caller(uid="anonymous")

# the domain of the flags of each unit, its full name; a test registers its own
DOMAINS: t.Final[dict[type[PermissionFlags], str]] = {
    AuthAttrsPermissions: "auth.profiles.attrs",
    AuthEmailCodePermissions: "auth.methods.email_code",
    AuthGroupsPermissions: "auth.access.groups",
    AuthMembersPermissions: "auth.access.members",
    AuthMetadataPermissions: "auth.metadata",
    AuthNicknamePermissions: "auth.methods.nickname",
    AuthSessionAttrsPermissions: "auth.sessions.attrs",
    AuthSessionPresetsPermissions: "auth.sessions.presets",
    AuthSignInPermissions: "auth.sign_in",
    AuthSignUpPermissions: "auth.sign_up",
    AuthTagsPermissions: "auth.profiles.tags",
    AuthTestingPermissions: "auth.methods.testing",
}


def masks(*items: PermissionFlags | Mapping[str, int]) -> Permissions:
    """The permissions of flags, each in the domain of its unit, and masks."""
    return Permissions(
        *(
            item if isinstance(item, Mapping) else {DOMAINS[type(item)]: int(item)}
            for item in items
        )
    )
