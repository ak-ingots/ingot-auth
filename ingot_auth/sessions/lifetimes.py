"""The strategies of the lifetime of the sessions."""

__all__ = ("AuthFixedLifetime", "BaseAuthSessionLifetime")

import abc
import datetime
import typing as t

from ingots.puer import Entity

from .items import AuthSessionCloseReason

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

    from .items import AuthSessionRecord


class BaseAuthSessionLifetime(Entity):
    """
    How long a session lives: the strategy in the slot ``lifetime`` of the
    sessions, which has none by default.
    """

    project: "AuthProject"

    @t.final
    def check(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        """The reason an open session expired for at the time, ``None`` if it lives."""
        return self._expire(session, now)

    @abc.abstractmethod
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        raise NotImplementedError(f"{type(self).__qualname__}._expire")


class AuthFixedLifetime(BaseAuthSessionLifetime):
    """
    A session lives ``AUTH_SESSION_TTL`` seconds from its sign-in, however
    used: then it expires, ``EXPIRED_ABSOLUTE``.
    """

    @t.override
    def _expire(
        self, session: "AuthSessionRecord", now: datetime.datetime
    ) -> AuthSessionCloseReason | None:
        ttl = datetime.timedelta(seconds=self.project.settings.configs.AUTH_SESSION_TTL)
        if now - session.opened_at >= ttl:
            return AuthSessionCloseReason.EXPIRED_ABSOLUTE
        return None
