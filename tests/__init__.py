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

from ingot_auth.access.groups import (
    AuthGroupsUnit,
)
from ingot_auth.access.members import (
    AuthMembersUnit,
)
from ingot_auth.metadata import (
    AuthMetadataUnit,
)
from ingot_auth.methods.email_code import (
    AuthEmailCodeMethod,
)
from ingot_auth.methods.nickname import (
    AuthNicknameMethod,
)
from ingot_auth.profiles import (
    AuthProfilesUnit,
)
from ingot_auth.profiles.attrs import (
    AuthAttrsUnit,
)
from ingot_auth.profiles.tags import (
    AuthTagsUnit,
)
from ingot_auth.sessions.attrs import (
    AuthSessionAttrsUnit,
)
from ingot_auth.sessions import (
    AuthSessionsUnit,
)
from ingot_auth.sessions.presets import (
    AuthSessionPresetsUnit,
)
from ingot_auth.sign_in import (
    AuthSignInUnit,
)
from ingot_auth.sign_up import (
    AuthSignUpUnit,
)
from ingot_auth.testing.methods import (
    AuthTestingMethod,
)

# the options of a command run by a test, as a fixture of ingots.testing
# configures its project: the configs not printed, the logging of the run kept
QUIET: t.Final = (
    *("--config", "IS_PRINT_CONFIGS=off"),
    *("--config", "IS_CONFIGURE_LOGGING=off"),
)
ROOT: t.Final = CallersProvider.ROOT
ANONYMOUS: t.Final = Caller(uid="anonymous")

# the domain of the flags of each unit, its full name; a test registers its own
DOMAINS: t.Final[dict[type[PermissionFlags], str]] = {
    AuthAttrsUnit.Flags: "auth.profiles.attrs",
    AuthEmailCodeMethod.Flags: "auth.methods.email_code",
    AuthGroupsUnit.Flags: "auth.access.groups",
    AuthMembersUnit.Flags: "auth.access.members",
    AuthMetadataUnit.Flags: "auth.metadata",
    AuthNicknameMethod.Flags: "auth.methods.nickname",
    AuthProfilesUnit.Flags: "auth.profiles",
    AuthSessionAttrsUnit.Flags: "auth.sessions.attrs",
    AuthSessionPresetsUnit.Flags: "auth.sessions.presets",
    AuthSessionsUnit.Flags: "auth.sessions",
    AuthSignInUnit.Flags: "auth.sign_in",
    AuthSignUpUnit.Flags: "auth.sign_up",
    AuthTagsUnit.Flags: "auth.profiles.tags",
    AuthTestingMethod.Flags: "auth.methods.testing",
}


def masks(*items: PermissionFlags | Mapping[str, int]) -> Permissions:
    """The permissions of flags, each in the domain of its unit, and masks."""
    return Permissions(
        *(
            item if isinstance(item, Mapping) else {DOMAINS[type(item)]: int(item)}
            for item in items
        )
    )


# what auth.grp_signed_in grants every signed-in user of its own: its sessions,
# its profile
OWN: t.Final = masks(
    AuthSessionsUnit.Flags.CAN_LIST_OWN,
    AuthSessionsUnit.Flags.CAN_REVOKE_OWN,
    AuthProfilesUnit.Flags.CAN_READ_OWN,
)
