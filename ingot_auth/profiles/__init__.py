"""
The profiles: the registries of what they hold, the tags and the attributes,
the values each profile has of them, which an operator sets, and the groups
of their work. The profiles themselves, their identities, their secrets and
their values are kept by the storages, :mod:`ingot_auth.storages`.
"""

__all__ = (
    "AuthGetOwnProfileOperation",
    "AuthOwnProfile",
    "AuthProfilesConsumersGroup",
    "AuthProfilesManagersGroup",
    "AuthProfilesUnit",
    "AuthSetProfileAttrValuesOperation",
    "AuthSetProfileAttrValuesParameters",
    "AuthSetProfileTagsOperation",
    "AuthSetProfileTagsParameters",
)

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access.groups import AuthGroupsOwner

from .attrs import AuthAttrsUnit
from .groups import AuthProfilesConsumersGroup, AuthProfilesManagersGroup
from .data import AuthOwnProfile
from .operations import (
    AuthGetOwnProfileOperation,
    AuthSetProfileAttrValuesOperation,
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsOperation,
    AuthSetProfileTagsParameters,
)
from .tags import AuthTagsUnit


class AuthProfilesUnit(AuthGroupsOwner, OperationsOwner, CliUnit):
    """
    The profiles: the registries of the tags and of the attributes, the
    values each profile has of them, set by an operator, the whole set each
    time, and the groups of their work, ``auth.profiles.grp_consumers``, who
    reads the registries, and ``auth.profiles.grp_managers``, who keeps them
    and sets the values.
    """

    class Flags(PermissionFlags):
        """
        The flags of the domain of the profiles, the full name of their unit,
        ``auth.profiles``: each kept for good, as the masks are stored and sent.
        ``auth.profiles.grp_managers`` grants the setting of their values,
        ``auth.grp_signed_in`` a signed-in user the reading of its own profile.
        """

        CAN_UPDATE = 1 << 0
        CAN_READ_OWN = 1 << 1

    cli_name = "profiles"
    cli_description = "The profiles of the users."

    grp_consumers = Slot(AuthProfilesConsumersGroup)
    grp_managers = Slot(AuthProfilesManagersGroup)

    permissions = PermissionsSlot(Flags)

    op_set_tags = Factory(AuthSetProfileTagsOperation)
    op_set_attr_values = Factory(AuthSetProfileAttrValuesOperation)
    op_get_own = Factory(AuthGetOwnProfileOperation)

    tags = Slot(AuthTagsUnit)
    attrs = Slot(AuthAttrsUnit)
