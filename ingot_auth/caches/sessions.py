"""
The cache of the open sessions, by the hash of the token, apart from their
callers, so that a caller is forgotten and formed again with its session kept.
"""

__all__ = ("BaseAuthSessionsCache",)

import abc
import datetime
import typing as t

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingot_auth.storages import AuthSessionRecord


class BaseAuthSessionsCache(Entity):
    """
    The open sessions, which a request finds here before the storage: what a
    backend of the cache implements.
    """

    @t.final
    async def get(self, token_hash: str) -> "AuthSessionRecord | None":
        """The session of the hash of a token, ``None`` if missed or expired."""
        return await self._get(token_hash)

    @t.final
    async def put(
        self, session: "AuthSessionRecord", expires_at: datetime.datetime
    ) -> None:
        """Keeps a session by the hash of its token until the time."""
        await self._put(session, expires_at)

    @t.final
    async def forget(self, token_hash: str) -> None:
        """Forgets the session of the hash of a token, if kept."""
        await self._forget(token_hash)

    @abc.abstractmethod
    async def _get(self, token_hash: str) -> "AuthSessionRecord | None":
        raise NotImplementedError(f"{type(self).__qualname__}._get")

    @abc.abstractmethod
    async def _put(
        self, session: "AuthSessionRecord", expires_at: datetime.datetime
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _forget(self, token_hash: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._forget")
