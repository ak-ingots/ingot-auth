"""
The storage of the secrets: what a profile is verified by later, the hash of
its password, one a profile, by its uid, whatever identifier it signs in by.
Apart from the identities, so a profile signed up with no password has none,
and a new one replaces the old alone.
"""

__all__ = ("BaseAuthSecretsStorage",)

import abc
import typing as t

from ingots.puer import Entity


class BaseAuthSecretsStorage(Entity):
    """
    The storage of the secrets: what a backend implements. A secret is as
    its maker makes it, a string the storage keeps as it is.
    """

    @t.final
    async def put(self, uid: str, secret: str) -> None:
        """Keeps the secret of a profile, in place of one there was."""
        await self._put(uid, secret)

    @t.final
    async def replace(self, uid: str, old: str, new: str) -> None:
        """
        Keeps ``new`` as the secret of a profile on the condition that it is
        still ``old``, the one read: a change of a password does not undo
        another made meanwhile.

        :raises AuthSecretChangedError: it is not ``old`` any more, or the
            profile has none.
        """
        await self._replace(uid, old, new)

    @t.final
    async def get(self, uid: str) -> str:
        """
        The secret of a profile.

        :raises AuthSecretNotFoundError: it has none.
        """
        return await self._get(uid)

    @abc.abstractmethod
    async def _put(self, uid: str, secret: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _replace(self, uid: str, old: str, new: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._replace")

    @abc.abstractmethod
    async def _get(self, uid: str) -> str:
        raise NotImplementedError(f"{type(self).__qualname__}._get")
