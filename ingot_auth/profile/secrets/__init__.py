"""
The secrets: what a method keeps to verify a subject later, the hash of a
password, say, by the method and the subject. Apart from the identities, so
a method with no secret has none, and a new one replaces the old alone.
"""

__all__ = ("AuthSecretNotFoundError", "BaseAuthSecretsStorage")

import abc
import typing as t

from ingots.puer import Entity

from ingot_auth.profile.identities import AuthIdentityError


class AuthSecretNotFoundError(AuthIdentityError):
    """The subject has no secret of the method."""

    @classmethod
    def for_method(cls, method: str) -> t.Self:
        return cls(f"{method}: the subject has no secret", method)


class BaseAuthSecretsStorage(Entity):
    """
    The storage of the secrets: what a backend implements. A secret is as
    the method makes it, a string the storage keeps as it is.
    """

    @t.final
    async def put(self, method: str, subject: str, secret: str) -> None:
        """Keeps the secret of a subject of a method, in place of one there was."""
        await self._put(method, subject, secret)

    @t.final
    async def get(self, method: str, subject: str) -> str:
        """
        The secret of a subject of a method.

        :raises AuthSecretNotFoundError: it has none.
        """
        return await self._get(method, subject)

    @abc.abstractmethod
    async def _put(self, method: str, subject: str, secret: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _get(self, method: str, subject: str) -> str:
        raise NotImplementedError(f"{type(self).__qualname__}._get")
