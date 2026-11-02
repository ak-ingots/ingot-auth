"""
The identities: who a profile is to a method, the subject of the method,
bound to the uid of the profile. A profile may have several, one a method.
"""

__all__ = (
    "AuthIdentity",
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
    "BaseAuthIdentitiesStorage",
)

import abc
import typing as t
from dataclasses import dataclass

from ingots.puer import Entity

from .errors import (
    AuthIdentityConflictError,
    AuthIdentityError,
    AuthIdentityNotFoundError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthIdentity:
    """The subject of a method, bound to a profile: unique within the method."""

    method: str
    subject: str
    uid: str


class BaseAuthIdentitiesStorage(Entity):
    """The storage of the identities: what a backend implements."""

    @t.final
    async def create(self, identity: AuthIdentity) -> None:
        """
        Binds a subject to a profile.

        :raises AuthIdentityConflictError: the subject of the method is bound.
        """
        await self._create(identity)

    @t.final
    async def find_uid(self, method: str, subject: str) -> str:
        """
        The uid of the profile a subject of a method is bound to.

        :raises AuthIdentityNotFoundError: it is bound to none.
        """
        return await self._find_uid(method, subject)

    @abc.abstractmethod
    async def _create(self, identity: AuthIdentity) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._create")

    @abc.abstractmethod
    async def _find_uid(self, method: str, subject: str) -> str:
        raise NotImplementedError(f"{type(self).__qualname__}._find_uid")
