"""The auth unit: the sign-up, the sign-in and the sessions of the project."""

__all__ = ("AuthUnit",)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.attrs import AuthAttrs
from ingot_auth.storage import AuthStorage
from ingot_auth.tags import AuthTags


class AuthUnit(CliUnit):
    """
    The auth of the project: the registries of the tags and the attributes,
    and the storage, abstract here: the project declares it with a backend
    in a subclass. The sign-up, the sign-in, the profiles and the sessions
    come as its slots.
    """

    cli_name = "auth"
    cli_description = "The auth of the users."

    storage = Slot(AuthStorage)
    tags = Slot(AuthTags)
    attrs = Slot(AuthAttrs)
