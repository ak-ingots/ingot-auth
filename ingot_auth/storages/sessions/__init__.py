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
from .data import (
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

    attrs = Slot(BaseAuthSessionAttrsStorage)  # type: ignore[type-abstract]
    presets = Slot(BaseAuthSessionPresetsStorage)  # type: ignore[type-abstract]

    @t.final
    async def open(self, session: AuthSessionRecord) -> None:
        """Keeps a new session, open: its uid and the hash of its token are new."""
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
        """
        The open sessions of a profile, in no order: the fastest a backend
        gives them; a consumer sorts them as it needs.
        """
        return await self._get_open(uid)

    @t.final
    async def get_all(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        """
        The sessions of a profile, open and closed, by the time they opened: the
        record of its sign-ins.
        """
        return await self._get_all(uid)

    @t.final
    async def get_all_open(
        self, after: str | None, limit: int
    ) -> tuple[AuthSessionRecord, ...]:
        """
        A page of the open sessions of every profile, by their uid: at most
        ``limit`` of them, those after the uid ``after``, the last of the page
        before, from the first if ``None``; none past the last.
        """
        return await self._get_all_open(after, limit)

    @t.final
    async def touch(self, session_uid: str, seen_at: datetime.datetime) -> None:
        """
        Writes the time an open session was seen at.

        :raises AuthSessionNotFoundError: no session of the uid is open.
        """
        await self._touch(session_uid, seen_at)

    @t.final
    async def close(
        self,
        session_uid: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        """
        Closes an open session for a reason, at a time; it stays kept, who
        closed it told by the activity log.

        :raises AuthSessionNotFoundError: no session of the uid is open.
        """
        await self._close(session_uid, reason, closed_at)

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
    async def _get_all(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_all")

    @abc.abstractmethod
    async def _get_all_open(
        self, after: str | None, limit: int
    ) -> tuple[AuthSessionRecord, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_all_open")

    @abc.abstractmethod
    async def _touch(self, session_uid: str, seen_at: datetime.datetime) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._touch")

    @abc.abstractmethod
    async def _close(
        self,
        session_uid: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._close")
