"""
The storage of the identities: what a profile signs in by, an identifier of
a kind, a nickname, an email, bound to the uid of the profile once, whatever
method uses it: the methods of an email find the same profile by the same
email. A profile may have several, one a kind.
"""

__all__ = ("BaseAuthIdentitiesStorage",)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthIdentity


class BaseAuthIdentitiesStorage(Entity):
    """The storage of the identities: what a backend implements."""

    @t.final
    async def create(self, identity: AuthIdentity) -> None:
        """
        Binds an identifier to a profile.

        :raises AuthIdentityConflictError: the identifier of the kind is bound.
        """
        await self._create(identity)

    @t.final
    async def find_uid(self, kind: str, value: str) -> str:
        """
        The uid of the profile an identifier of a kind is bound to.

        :raises AuthIdentityNotFoundError: it is bound to none.
        """
        return await self._find_uid(kind, value)

    @abc.abstractmethod
    async def _create(self, identity: AuthIdentity) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._create")

    @abc.abstractmethod
    async def _find_uid(self, kind: str, value: str) -> str:
        raise NotImplementedError(f"{type(self).__qualname__}._find_uid")
