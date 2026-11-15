"""
The profiles: the registries of what they hold, the tags and the attributes,
the values each profile has of them, which an operator sets, and the groups
of their work. The profiles themselves, their identities, their secrets and
their values are kept by the storages, :mod:`ingot_auth.storages`.
"""

__all__ = (
    "AuthProfilesConsumersGroup",
    "AuthProfilesManagersGroup",
    "AuthProfilesPermissions",
    "AuthProfilesUnit",
    "AuthSetProfileAttrValuesOperation",
    "AuthSetProfileAttrValuesParameters",
    "AuthSetProfileTagsOperation",
    "AuthSetProfileTagsParameters",
)

from ingots.defaults.operations import OperationsOwner, PermissionsSlot
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access.groups import AuthGroupsOwner

from .attrs import AuthAttrsUnit
from .groups import AuthProfilesConsumersGroup, AuthProfilesManagersGroup
from .items import AuthSetProfileAttrValuesParameters, AuthSetProfileTagsParameters
from .operations import AuthSetProfileAttrValuesOperation, AuthSetProfileTagsOperation
from .permissions import AuthProfilesPermissions
from .tags import AuthTagsUnit


class AuthProfilesUnit(AuthGroupsOwner, OperationsOwner, CliUnit):
    """
    The profiles: the registries of the tags and of the attributes, the
    values each profile has of them, set by an operator, the whole set each
    time, and the groups of their work, ``auth.profiles.grp_consumers``, who
    reads the registries, and ``auth.profiles.grp_managers``, who keeps them
    and sets the values.
    """

    cli_name = "profiles"
    cli_description = "The profiles of the users."

    grp_consumers = Slot(AuthProfilesConsumersGroup)
    grp_managers = Slot(AuthProfilesManagersGroup)

    permissions = PermissionsSlot(AuthProfilesPermissions)

    op_set_tags = Factory(AuthSetProfileTagsOperation)
    op_set_attr_values = Factory(AuthSetProfileAttrValuesOperation)

    tags = Slot(AuthTagsUnit)
    attrs = Slot(AuthAttrsUnit)
