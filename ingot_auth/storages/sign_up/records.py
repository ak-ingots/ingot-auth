"""The storage of the records of the sign-ups."""

__all__ = ("BaseAuthSignUpRecordsStorage",)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthSignUpRecord


class BaseAuthSignUpRecordsStorage(Entity):
    """The records of the sign-ups, one a profile: what a backend implements."""

    @t.final
    async def add(self, record: AuthSignUpRecord) -> None:
        """Keeps the record of a sign-up."""
        await self._add(record)

    @t.final
    async def get(self, uid: str) -> AuthSignUpRecord:
        """
        The record of the sign-up of a profile.

        :raises AuthSignUpRecordNotFoundError: there is none.
        """
        return await self._get(uid)

    @abc.abstractmethod
    async def _add(self, record: AuthSignUpRecord) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._add")

    @abc.abstractmethod
    async def _get(self, uid: str) -> AuthSignUpRecord:
        raise NotImplementedError(f"{type(self).__qualname__}._get")
