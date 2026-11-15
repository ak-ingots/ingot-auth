"""
The profiles: the registries of what they hold, the tags and the attributes,
and the groups of their work. The profiles themselves, their identities and
their secrets are kept by the storages, :mod:`ingot_auth.storages`.
"""

__all__ = (
    "AuthProfilesConsumersGroup",
    "AuthProfilesManagersGroup",
    "AuthProfilesUnit",
)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access.groups import AuthGroupsOwner

from .attrs import AuthAttrsUnit
from .groups import AuthProfilesConsumersGroup, AuthProfilesManagersGroup
from .tags import AuthTagsUnit


class AuthProfilesUnit(AuthGroupsOwner, CliUnit):
    """
    The profiles: the registries of the tags and of the attributes, and the
    groups of their work, ``auth.profiles.grp_consumers``, who reads them, and
    ``auth.profiles.grp_managers``, who keeps them.
    """

    cli_name = "profiles"
    cli_description = "The profiles of the users."

    grp_consumers = Slot(AuthProfilesConsumersGroup)
    grp_managers = Slot(AuthProfilesManagersGroup)

    tags = Slot(AuthTagsUnit)
    attrs = Slot(AuthAttrsUnit)
