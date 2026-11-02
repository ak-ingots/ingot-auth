"""The storage of the sign-up: its records."""

__all__ = (
    "AuthSignUpRecordNotFoundError",
    "AuthSignUpStorage",
    "BaseAuthSignUpRecordsStorage",
)

import abc
import typing as t

from ingots.puer import Entity, Slot, Unit

from .errors import AuthSignUpRecordNotFoundError
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


class AuthSignUpStorage(Unit):
    """The storage of the sign-up, every part of it abstract."""

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    records = Slot(BaseAuthSignUpRecordsStorage)  # type: ignore[type-abstract]
