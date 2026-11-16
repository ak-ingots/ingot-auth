"""The storage of the sessions in memory."""

__all__ = (
    "AuthMemorySessionAttrsStorage",
    "AuthMemorySessionPresetsStorage",
    "AuthMemorySessionsStorage",
)

import dataclasses
import datetime
import typing as t

from ingots.puer import Slot

from ingot_auth.storages import (
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
    AuthSessionsStorage,
)

from ..state import AuthMemoryStateMixin
from .attrs import AuthMemorySessionAttrsStorage
from .presets import AuthMemorySessionPresetsStorage


class AuthMemorySessionsStorage(AuthMemoryStateMixin, AuthSessionsStorage):
    """The storage of the sessions in memory: the sessions by their ids."""

    attrs = Slot(AuthMemorySessionAttrsStorage)
    presets = Slot(AuthMemorySessionPresetsStorage)

    def __init__(self) -> None:
        super().__init__()
        self._sessions: dict[str, AuthSessionRecord] = {}

    @t.override
    async def _open(self, session: AuthSessionRecord) -> None:
        self._sessions[session.uid] = session

    @t.override
    async def _find(self, token_hash: str) -> AuthSessionRecord:
        for session in self._sessions.values():
            if session.token_hash == token_hash and session.closed_at is None:
                return session
        raise AuthSessionNotFoundError.for_token()

    @t.override
    async def _get_open(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        return tuple(
            sorted(
                (
                    session
                    for session in self._sessions.values()
                    if session.profile_uid == uid and session.closed_at is None
                ),
                key=lambda session: (session.opened_at, session.uid),
            )
        )

    @t.override
    async def _get_all(self, uid: str) -> tuple[AuthSessionRecord, ...]:
        return tuple(
            sorted(
                (
                    session
                    for session in self._sessions.values()
                    if session.profile_uid == uid
                ),
                key=lambda session: (session.opened_at, session.uid),
            )
        )

    @t.override
    async def _get_all_open(
        self, after: str | None, limit: int
    ) -> tuple[AuthSessionRecord, ...]:
        found = sorted(
            (
                session
                for session in self._sessions.values()
                if session.closed_at is None and (after is None or session.uid > after)
            ),
            key=lambda session: session.uid,
        )
        return tuple(found[:limit])

    @t.override
    async def _touch(self, session_uid: str, seen_at: datetime.datetime) -> None:
        session = self._find_open(session_uid)
        self._sessions[session_uid] = dataclasses.replace(session, seen_at=seen_at)

    @t.override
    async def _close(
        self,
        session_uid: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        session = self._find_open(session_uid)
        self._sessions[session_uid] = dataclasses.replace(
            session, closed_at=closed_at, close_reason=reason
        )

    def _find_open(self, session_uid: str) -> AuthSessionRecord:
        """:raises AuthSessionNotFoundError: no session of the id is open."""
        session = self._sessions.get(session_uid)
        if session is None or session.closed_at is not None:
            raise AuthSessionNotFoundError.for_uid(session_uid)
        return session
