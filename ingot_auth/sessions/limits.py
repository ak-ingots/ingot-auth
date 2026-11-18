"""The strategies of the limit of the open sessions of a profile."""

__all__ = (
    "AuthEvictOldestLimit",
    "AuthNoLimit",
    "AuthRefuseLimit",
    "BaseAuthMaxSessionsLimit",
    "BaseAuthSessionsLimit",
)

import abc
import datetime
import typing as t

from ingots.puer import Entity

from ingot_auth.storages import (
    AuthActivityAction,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)

from .errors import AuthSessionsLimitError

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    from ingots.defaults.operations import OperationMetadata

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthSessionRecord

    from . import AuthSessionsUnit


class BaseAuthSessionsLimit(Entity):
    """
    What a sign-in does to the open sessions of a profile before it opens
    one: the strategy in the slot ``limit`` of the sessions, which has none
    by default.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.final
    async def make_room(
        self, uid: str, now: datetime.datetime, metadata: "OperationMetadata"
    ) -> "tuple[AuthSessionRecord, ...]":
        """
        Makes room for the session a sign-in of a profile opens, in its
        transaction: gives the sessions it closed, for the cache to forget
        after the commit.

        :raises AuthSessionsLimitError: the strategy refuses the sign-in.
        """
        return await self._make_room(uid, now, metadata)

    @abc.abstractmethod
    async def _make_room(
        self, uid: str, now: datetime.datetime, metadata: "OperationMetadata"
    ) -> "tuple[AuthSessionRecord, ...]":
        raise NotImplementedError(f"{type(self).__qualname__}._make_room")


class AuthNoLimit(BaseAuthSessionsLimit):
    """As many sessions as the users open: none read, none closed."""

    @t.override
    async def _make_room(
        self, uid: str, now: datetime.datetime, metadata: "OperationMetadata"
    ) -> "tuple[AuthSessionRecord, ...]":
        return ()


class BaseAuthMaxSessionsLimit(BaseAuthSessionsLimit):
    """
    A profile keeps ``AUTH_SESSIONS_MAX`` open sessions, at least one: how
    many is of the operator, the config; which of them give way to a new
    one, or whether it is refused, of the strategy extending this one.
    """

    @t.override
    async def _make_room(
        self, uid: str, now: datetime.datetime, metadata: "OperationMetadata"
    ) -> "tuple[AuthSessionRecord, ...]":
        """
        The open sessions the lifetime tells expired take no room, left to
        their requests and the sweep to close; of the rest, as many as the
        limit or more, those the strategy picks closed ``EVICTED``, a record
        ``evict`` each, in the run of the sign-in. Two sign-ins at once may
        leave one session over: a soft limit.
        """
        sessions = await self.project.auth.storage.sessions.get_open(uid)
        limit = max(self.project.settings.configs.AUTH_SESSIONS_MAX, 1)
        if len(sessions) < limit:
            return ()
        lifetime = self.parent.lifetime
        alive = tuple(
            session for session in sessions if lifetime.check(session, now) is None
        )
        excess = len(alive) - limit + 1  # the session the sign-in opens
        if excess <= 0:
            return ()
        return await self._evict(self._select_evicted(alive, excess), now, metadata)

    @abc.abstractmethod
    def _select_evicted(
        self, alive: "tuple[AuthSessionRecord, ...]", excess: int
    ) -> "Sequence[AuthSessionRecord]":
        """
        The sessions to evict of the open ones alive, in no order, ``excess``
        of them to keep within the limit; or raises to refuse. The strategy
        orders them by its own sign.
        """
        raise NotImplementedError(f"{type(self).__qualname__}._select_evicted")

    @t.final
    async def _evict(
        self,
        sessions: "Sequence[AuthSessionRecord]",
        now: datetime.datetime,
        metadata: "OperationMetadata",
    ) -> "tuple[AuthSessionRecord, ...]":
        storage = self.project.auth.storage
        evicted = []
        for session in sessions:
            try:
                await storage.sessions.close(
                    session.uid, AuthSessionCloseReason.EVICTED, now
                )
            except AuthSessionNotFoundError:
                continue  # closed meanwhile, by another request
            await self.project.auth.activities.record(
                self.parent, session.uid, AuthActivityAction.EVICT, metadata
            )
            evicted.append(session)
        return tuple(evicted)


class AuthEvictOldestLimit(BaseAuthMaxSessionsLimit):
    """
    Signs out the sessions seen longest ago: a user who lost a device is not
    locked out; with ``AUTH_SESSIONS_MAX=1``, a later sign-in signs out an
    earlier one, as a game keeps one session a player.
    """

    @t.override
    def _select_evicted(
        self, alive: "tuple[AuthSessionRecord, ...]", excess: int
    ) -> "Sequence[AuthSessionRecord]":
        return sorted(alive, key=lambda session: session.seen_at)[:excess]


class AuthRefuseLimit(BaseAuthMaxSessionsLimit):
    """Refuses the sign-in: the user signs out of another session first."""

    @t.override
    def _select_evicted(
        self, alive: "tuple[AuthSessionRecord, ...]", excess: int
    ) -> "Sequence[AuthSessionRecord]":
        raise AuthSessionsLimitError.for_count(len(alive))
