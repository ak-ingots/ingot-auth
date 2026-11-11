"""The storage of the profiles."""

__all__ = (
    "AuthAttr",
    "AuthIdentity",
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
    "AuthProfile",
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
    "AuthProfilesStorage",
    "AuthSecretNotFoundError",
    "AuthTag",
    "BaseAuthAttrsStorage",
    "BaseAuthIdentitiesStorage",
    "BaseAuthSecretsStorage",
    "BaseAuthTagsStorage",
)

import abc
import typing as t

from ingots.puer import Slot, Unit

from .attrs import BaseAuthAttrsStorage
from .errors import (
    AuthIdentityConflictError,
    AuthIdentityError,
    AuthIdentityNotFoundError,
    AuthProfileConflictError,
    AuthProfileError,
    AuthProfileNotFoundError,
    AuthSecretNotFoundError,
)
from .identities import BaseAuthIdentitiesStorage
from .items import AuthAttr, AuthIdentity, AuthProfile, AuthTag
from .secrets import BaseAuthSecretsStorage
from .tags import BaseAuthTagsStorage


class AuthProfilesStorage(Unit):
    """
    The storage of the profiles: the profiles themselves, what a backend
    implements, and as slots the registries, the identities of the profiles
    and the secrets of these, each abstract.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    tags = Slot(BaseAuthTagsStorage)  # type: ignore[type-abstract]
    attrs = Slot(BaseAuthAttrsStorage)  # type: ignore[type-abstract]
    identities = Slot(BaseAuthIdentitiesStorage)  # type: ignore[type-abstract]
    secrets = Slot(BaseAuthSecretsStorage)  # type: ignore[type-abstract]

    @t.final
    async def create(self, profile: AuthProfile) -> None:
        """
        Stores a new profile.

        :raises AuthProfileConflictError: its uid is taken.
        """
        await self._create(profile)

    @t.final
    async def get(self, uid: str) -> AuthProfile:
        """
        The profile of a uid.

        :raises AuthProfileNotFoundError: no profile has it.
        """
        return await self._get(uid)

    @abc.abstractmethod
    async def _create(self, profile: AuthProfile) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._create")

    @abc.abstractmethod
    async def _get(self, uid: str) -> AuthProfile:
        raise NotImplementedError(f"{type(self).__qualname__}._get")
