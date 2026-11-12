"""The strategies of the lifetime of the sessions."""

__all__ = (
    "AuthFixedLifetime",
    "AuthSlidingFixedLifetime",
    "AuthSlidingLifetime",
    "BaseAuthSessionLifetime",
)

import abc
import datetime
import typing as t

from ingots.puer import Entity

from ingot_auth.storages import AuthSessionCloseReason

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthSessionRecord


class BaseAuthSessionLifetime(Entity):
    """
    How long a session lives: the strategy in the slot ``lifetime`` of the
    sessions, which has none by default. Given a session and the time, it
    tells whether the session expired and why, and whether the time it is
    seen at is to be written.
    """

    project: "AuthProject"

    @t.final
    def check(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        """The reason an open session expired for at the time, ``None`` if it lives."""
        return self._expire(session, now)

    @t.final
    def is_touch_due(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> bool:
        """Whether the time a living session is seen at is to be written."""
        return self._is_touch_due(session, now)

    @abc.abstractmethod
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        raise NotImplementedError(f"{type(self).__qualname__}._expire")

    def _is_touch_due(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> bool:
        """Never here: a lifetime that does not read the time seen."""
        return False


class AuthFixedLifetime(BaseAuthSessionLifetime):
    """
    A session lives ``AUTH_SESSION_TTL`` seconds from its sign-in, however
    used: then it expires, ``EXPIRED_ABSOLUTE``.
    """

    @t.override
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        if now >= self._get_absolute_end(session):
            return AuthSessionCloseReason.EXPIRED_ABSOLUTE
        return None

    @t.final
    def _get_absolute_end(self, session: "AuthSessionRecord") -> datetime.datetime:
        ttl = self.project.settings.configs.AUTH_SESSION_TTL
        return session.opened_at + datetime.timedelta(seconds=ttl)


class AuthSlidingLifetime(BaseAuthSessionLifetime):
    """
    A session lives while used: idle ``AUTH_SESSION_IDLE_TTL`` seconds, it
    expires, ``EXPIRED_IDLE``. The time it is seen at is written at most once
    per ``AUTH_SESSION_TOUCH_INTERVAL`` seconds, not on every request, so the
    idle limit is precise to that interval, which stays well below it. It
    has no overall limit, which the guides ask for: with one,
    :class:`AuthSlidingFixedLifetime`.
    """

    @t.override
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        if now >= self._get_idle_end(session):
            return AuthSessionCloseReason.EXPIRED_IDLE
        return None

    @t.override
    def _is_touch_due(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> bool:
        interval = self.project.settings.configs.AUTH_SESSION_TOUCH_INTERVAL
        return now - session.seen_at >= datetime.timedelta(seconds=interval)

    @t.final
    def _get_idle_end(self, session: "AuthSessionRecord") -> datetime.datetime:
        ttl = self.project.settings.configs.AUTH_SESSION_IDLE_TTL
        return session.seen_at + datetime.timedelta(seconds=ttl)


class AuthSlidingFixedLifetime(AuthSlidingLifetime, AuthFixedLifetime):
    """
    A session lives while used, ``AUTH_SESSION_IDLE_TTL`` seconds idle at
    most, and ``AUTH_SESSION_TTL`` seconds from its sign-in at most: it
    expires by whichever comes first, ``EXPIRED_IDLE`` or
    ``EXPIRED_ABSOLUTE``. The time it is seen at is written as the sliding
    one writes it, ``AUTH_SESSION_TOUCH_INTERVAL``.
    """

    @t.override
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        end, reason = min(
            (self._get_absolute_end(session), AuthSessionCloseReason.EXPIRED_ABSOLUTE),
            (self._get_idle_end(session), AuthSessionCloseReason.EXPIRED_IDLE),
            key=lambda pair: pair[0],
        )
        return reason if now >= end else None
