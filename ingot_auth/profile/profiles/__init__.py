"""The profiles themselves: a uid each, the sign-up creating it."""

__all__ = (
    "AuthProfile",
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
    "BaseAuthProfilesStorage",
)

import abc
import datetime
import typing as t
from dataclasses import dataclass

from ingots.puer import Entity

from .errors import AuthProfileConflictError, AuthProfileError, AuthProfileNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfile:
    """
    A profile: ``uid`` is what the rest of an application knows the user by.
    The values of its tags and attributes come in another change.
    """

    uid: str
    created_at: datetime.datetime


class BaseAuthProfilesStorage(Entity):
    """The storage of the profiles: what a backend implements."""

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
