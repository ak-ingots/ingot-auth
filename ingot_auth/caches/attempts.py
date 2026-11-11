"""The cache of the attempts: a sign-up, a sign-in between its steps."""

__all__ = ("BaseAuthAttemptsCache",)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthAttempt


class BaseAuthAttemptsCache(Entity):
    """
    The attempts, which live a few minutes: what a backend of the cache
    implements. An attempt is taken once, so two answers to it never both
    proceed.
    """

    @t.final
    async def put(self, attempt: AuthAttempt) -> None:
        """Keeps an attempt until it expires, in place of one of its id."""
        await self._put(attempt)

    @t.final
    async def take(self, attempt_id: str) -> AuthAttempt:
        """
        Gives an attempt and forgets it.

        :raises AuthAttemptNotFoundError: no attempt has the id, or it expired.
        """
        return await self._take(attempt_id)

    @abc.abstractmethod
    async def _put(self, attempt: AuthAttempt) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._put")

    @abc.abstractmethod
    async def _take(self, attempt_id: str) -> AuthAttempt:
        raise NotImplementedError(f"{type(self).__qualname__}._take")
