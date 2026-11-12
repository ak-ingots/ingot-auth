"""The storage of the sessions."""

__all__ = (
    "AuthSessionAttr",
    "AuthSessionAttrSource",
    "AuthSessionCloseReason",
    "AuthSessionError",
    "AuthSessionNotFoundError",
    "AuthSessionPreset",
    "AuthSessionPresetBinding",
    "AuthSessionRecord",
    "AuthSessionsStorage",
    "BaseAuthSessionAttrsStorage",
    "BaseAuthSessionPresetsStorage",
)

import abc
import datetime
import typing as t

from ingots.puer import Slot, Unit

from .attrs import BaseAuthSessionAttrsStorage
from .errors import AuthSessionError, AuthSessionNotFoundError
from .items import (
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionCloseReason,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    AuthSessionRecord,
)
from .presets import BaseAuthSessionPresetsStorage


class AuthSessionsStorage(Unit):
    """
    The storage of the sessions: the sessions themselves, what a backend
    implements, kept closed too, as the records of the sign-ins, and as slots
    the registries, each abstract.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    attrs = Slot(BaseAuthSessionAttrsStorage)  # type: ignore[type-abstract]
    presets = Slot(BaseAuthSessionPresetsStorage)  # type: ignore[type-abstract]

    @t.final
    async def open(self, session: AuthSessionRecord) -> None:
        """Keeps a new session, open: its id and the hash of its token are new."""
        await self._open(session)

    @t.final
    async def find(self, token_hash: str) -> AuthSessionRecord:
        """
        The open session of the hash of a token.

        :raises AuthSessionNotFoundError: none is open with it.
        """
        return await self._find(token_hash)

    @t.final
    async def get_open(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        """The open sessions of a profile, by the time they opened."""
        return await self._get_open(uid)

    @t.final
    async def close(
        self,
        session_id: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        """
        Closes an open session for a reason, at a time; it stays kept.

        :raises AuthSessionNotFoundError: no session of the id is open.
        """
        await self._close(session_id, reason, closed_at)

    @abc.abstractmethod
    async def _open(self, session: AuthSessionRecord) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._open")

    @abc.abstractmethod
    async def _find(self, token_hash: str) -> AuthSessionRecord:
        raise NotImplementedError(f"{type(self).__qualname__}._find")

    @abc.abstractmethod
    async def _get_open(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_open")

    @abc.abstractmethod
    async def _close(
        self,
        session_id: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._close")
