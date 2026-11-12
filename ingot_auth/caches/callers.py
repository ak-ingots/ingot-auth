"""
The cache of the callers of the open sessions, by the hash of the token and the
digest of the groups, apart from the sessions, so that a caller is forgotten
and formed again with its session kept.
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
    cache only: what a backend of the cache implements. A caller is kept by the
    hash of the token of its session and the digest of the groups it was formed
    by, so that one formed by other groups, before a deploy, is missed.
    """

    @t.final
    async def get(self, token_hash: str, groups_digest: str) -> AuthCaller | None:
        """
        The caller of the hash of a token formed by the groups of a digest,
        ``None`` if missed or expired.
        """
        return await self._get(token_hash, groups_digest)

    @t.final
    async def put(
        self,
        token_hash: str,
        groups_digest: str,
        caller: AuthCaller,
        expires_at: datetime.datetime,
    ) -> None:
        """
        Keeps the caller of the hash of a token, formed by the groups of a
        digest, until the time.
        """
        await self._put(token_hash, groups_digest, caller, expires_at)

    @t.final
    async def forget(self, token_hash: str, groups_digest: str) -> None:
        """
        Forgets the caller of the hash of a token formed by the groups of a
        digest, if kept.
        """
        await self._forget(token_hash, groups_digest)

    @abc.abstractmethod
    async def _get(self, token_hash: str, groups_digest: str) -> AuthCaller | None:
        raise NotImplementedError(f"{type(self).__qualname__}._get")

    @abc.abstractmethod
    async def _put(
        self,
        token_hash: str,
        groups_digest: str,
        caller: AuthCaller,
        expires_at: datetime.datetime,
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _forget(self, token_hash: str, groups_digest: str) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._forget")
