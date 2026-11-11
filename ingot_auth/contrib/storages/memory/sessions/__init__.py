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

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemorySessionsStorage(AuthMemoryStateMixin, AuthSessionsStorage):
    """The storage of the sessions in memory: the sessions by their ids."""

    attrs = Slot(AuthMemorySessionAttrsStorage)
    presets = Slot(AuthMemorySessionPresetsStorage)

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._sessions: dict[str, AuthSessionRecord] = {}

    @t.override
    async def _open(self, session: AuthSessionRecord) -> None:
        self._sessions[session.id] = session

    @t.override
    async def _find(self, token_hash: str) -> AuthSessionRecord:
        for session in self._sessions.values():
            if session.token_hash == token_hash and session.closed_at is None:
                return session
        raise AuthSessionNotFoundError.for_token()

    @t.override
    async def _close(
        self,
        session_id: str,
        reason: AuthSessionCloseReason,
        closed_at: datetime.datetime,
    ) -> None:
        session = self._sessions.get(session_id)
        if session is None or session.closed_at is not None:
            raise AuthSessionNotFoundError.for_id(session_id)
        self._sessions[session_id] = dataclasses.replace(
            session, closed_at=closed_at, close_reason=reason
        )
