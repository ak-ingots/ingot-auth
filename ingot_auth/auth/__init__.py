"""The auth unit: the sign-up, the sign-in and the sessions of the project."""

__all__ = ("AuthUnit",)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.cache import AuthCache
from ingot_auth.metadata import AuthMetadataUnit
from ingot_auth.methods import AuthMethods
from ingot_auth.policies import AuthPolicies
from ingot_auth.profiles import AuthProfiles
from ingot_auth.sessions import AuthSessions
from ingot_auth.sign_up import AuthSignUpUnit
from ingot_auth.storage import AuthStorage


class AuthUnit(CliUnit):
    """
    The auth of the project: the profiles and the sessions, each with its
    registries, the methods, none here, the policies of what a user types
    and their presets, the sign-up, the metadata, and the
    storage and the cache, abstract here: the project declares them with a
    backend in a subclass. The sign-in and the sessions themselves come as
    its slots.
    """

    cli_name = "auth"
    cli_description = "The auth of the users."

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    storage = Slot(AuthStorage)  # type: ignore[type-abstract]
    cache = Slot(AuthCache)
    methods = Slot(AuthMethods)
    policies = Slot(AuthPolicies)
    profiles = Slot(AuthProfiles)
    sessions = Slot(AuthSessions)
    sign_up = Slot(AuthSignUpUnit)
    metadata = Slot(AuthMetadataUnit)
