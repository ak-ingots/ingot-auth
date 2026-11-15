"""The auth unit: the sign-up, the sign-in and the sessions of the project."""

__all__ = ("AuthUnit",)

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import (
    AuthAnonymousGroup,
    AuthGroupsOwner,
    AuthSignedInGroup,
)
from ingot_auth.caches import AuthCache
from ingot_auth.dispatchers import BaseAuthDispatcher
from ingot_auth.mailers import BaseAuthMailer
from ingot_auth.metadata import AuthMetadataUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.profiles import AuthProfilesUnit
from ingot_auth.sessions import AuthSessionsUnit
from ingot_auth.sign_in import AuthSignInUnit
from ingot_auth.sign_up import AuthSignUpUnit
from ingot_auth.storages import AuthStorage


class AuthUnit(AuthGroupsOwner, CliUnit):
    """
    The auth of the project: the profiles and the sessions, each with its
    registries, the access, the groups of the users and their members, the
    methods, none here, with the policies of what a user types, the sign-up,
    the sign-in, the metadata, and the storage, the cache, the dispatcher of
    the operations run in the background and the mailer, abstract here: the
    project declares them with a backend in a subclass. Its groups are of
    the whole auth: ``auth.grp_anonymous``, of every caller that tells no one,
    and ``auth.grp_signed_in``, of every signed-in user, neither keeping
    members.
    """

    cli_name = "auth"
    cli_description = "The auth of the users."

    grp_anonymous = Slot(AuthAnonymousGroup)
    grp_signed_in = Slot(AuthSignedInGroup)

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    storage = Slot(AuthStorage)  # type: ignore[type-abstract]
    cache = Slot(AuthCache)
    dispatcher = Slot(BaseAuthDispatcher)  # type: ignore[type-abstract]
    mailer = Slot(BaseAuthMailer)  # type: ignore[type-abstract]
    methods = Slot(AuthMethodsUnit)
    profiles = Slot(AuthProfilesUnit)
    sessions = Slot(AuthSessionsUnit)
    access = Slot(AuthAccessUnit)
    sign_up = Slot(AuthSignUpUnit)
    sign_in = Slot(AuthSignInUnit)
    metadata = Slot(AuthMetadataUnit)
