"""The attempts: a sign-up, a sign-in between its steps."""

__all__ = ("AuthAttempt", "BaseAuthAttemptsCache")

import abc
import datetime
import typing as t
from dataclasses import dataclass

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttempt:
    """
    A flow waiting for an answer: ``id`` is what the client holds, random, the
    rest stays with the server. ``values`` are those of the attributes of the
    session the client started with; ``failures`` the answers refused so far.
    """

    id: str
    flow: str
    method: str
    state: object
    values: "Mapping[int, AuthAttrValue]"
    expires_at: datetime.datetime
    failures: int = 0


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
