"""The auth unit: the sign-up, the sign-in and the sessions of the project."""

__all__ = ("AuthUnit",)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.metadata import AuthMetadataUnit
from ingot_auth.profile import AuthProfileUnit
from ingot_auth.session import AuthSessionUnit
from ingot_auth.storage import AuthStorage


class AuthUnit(CliUnit):
    """
    The auth of the project: the profiles and the sessions, each with its
    registries, the metadata, and the storage, abstract here: the project
    declares it with a backend in a subclass. The sign-up, the sign-in and
    the sessions themselves come as its slots.
    """

    cli_name = "auth"
    cli_description = "The auth of the users."

    storage = Slot(AuthStorage)
    profile = Slot(AuthProfileUnit)
    session = Slot(AuthSessionUnit)
    metadata = Slot(AuthMetadataUnit)
