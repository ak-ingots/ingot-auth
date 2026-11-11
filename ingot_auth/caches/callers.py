"""
The cache of the callers of the open sessions, by the hash of the token, apart
from the sessions, so that a caller is forgotten and formed again with its
session kept.
"""

__all__ = ("BaseAuthCallersCache",)

import abc
import datetime
import typing as t

from ingots.puer import Entity

from .items import AuthCaller


class BaseAuthCallersCache(Entity):
    """
    The callers of the open sessions, with their permissions, which live in the
    cache only: what a backend of the cache implements.
    """

    @t.final
    async def get(self, token_hash: str) -> AuthCaller | None:
        """The caller of the hash of a token, ``None`` if missed or expired."""
        return await self._get(token_hash)

    @t.final
    async def put(
        self, token_hash: str, caller: AuthCaller, expires_at: datetime.datetime
    ) -> None:
        """Keeps the caller of the hash of a token until the time."""
        await self._put(token_hash, caller, expires_at)

    @t.final
    async def forget(self, token_hash: str) -> None:
        """Forgets the caller of the hash of a token, if kept."""
        await self._forget(token_hash)

    @abc.abstractmethod
    async def _get(self, token_hash: str) -> AuthCaller | None:
        raise NotImplementedError(f"{type(self).__qualname__}._get")

    @abc.abstractmethod
    async def _put(
        self, token_hash: str, caller: AuthCaller, expires_at: datetime.datetime
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _forget(self, token_hash: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._forget")
