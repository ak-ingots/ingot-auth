"""
The storage of the activity log: the records of the changes of state, kept
as written, appended and found, never changed.
"""

__all__ = (
    "AuthActivityAction",
    "AuthActivityQuery",
    "AuthActivityRecord",
    "BaseAuthActivitiesStorage",
)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthActivityAction, AuthActivityQuery, AuthActivityRecord


class BaseAuthActivitiesStorage(Entity):
    """
    The storage of the activity log: what a backend implements. A record is
    appended in the transaction open, if one is, as the change it tells; the
    context a map of plain values, numbers, texts, decimals, times, lists and
    maps of them, given back as kept.
    """

    @t.final
    async def append(self, record: AuthActivityRecord) -> None:
        """Keeps a record."""
        await self._append(record)

    @t.final
    async def find(self, query: AuthActivityQuery) -> tuple[AuthActivityRecord, ...]:
        """The records the query matches, the newest first, as many as its limit."""
        return await self._find(query)

    @abc.abstractmethod
    async def _append(self, record: AuthActivityRecord) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._append")

    @abc.abstractmethod
    async def _find(self, query: AuthActivityQuery) -> tuple[AuthActivityRecord, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._find")
