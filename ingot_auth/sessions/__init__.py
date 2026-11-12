"""
The sessions: what a sign-in opens and a token stands for, the caller of a
request, with the registry of the attributes of what a sign-up, a sign-in
happened on and the presets asking for them. Their storage is in
:mod:`ingot_auth.storages`, their caches in :mod:`ingot_auth.caches`.
"""

__all__ = (
    "AuthFixedLifetime",
    "AuthSessionExpiredError",
    "AuthSessionToken",
    "AuthSessionsUnit",
    "BaseAuthSessionLifetime",
)

import datetime
import hashlib
import os
import secrets
import typing as t

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from ingot_auth.caches import AuthCaller
from ingot_auth.storages import (
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
)

from .attrs import AuthSessionAttrsUnit
from .errors import AuthSessionExpiredError
from .items import AuthSessionToken
from .lifetimes import AuthFixedLifetime, BaseAuthSessionLifetime
from .presets import AuthSessionPresetsUnit

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue


class AuthSessionsUnit(CliUnit):
    """
    The sessions: the registries of their attributes and of the presets, and
    the strategy of their lifetime in the slot ``lifetime``, none by default,
    which a project declares. A sign-in opens a session and gives its token;
    a request brings the token, and :meth:`authenticate` turns it into the
    caller, from the cache, or from the storage and the access on a miss. A
    change of what a caller holds forgets the callers of the profile,
    :meth:`forget_callers`.
    """

    cli_name = "sessions"
    cli_description = "The sessions of the users."

    project: "AuthProject"

    attrs = Slot(AuthSessionAttrsUnit)
    presets = Slot(AuthSessionPresetsUnit)
    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    lifetime = Slot(BaseAuthSessionLifetime)  # type: ignore[type-abstract]

    @t.final
    async def open(
        self, uid: str, method: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> AuthSessionToken:
        """
        Opens a session of a profile signed in by a method, with the values of
        the attributes of the session, checked by the caller, and gives its
        token, 256 random bits, given once, kept by none but the client, with
        the id of the session.
        """
        token = secrets.token_urlsafe(32)
        session = AuthSessionRecord(
            id=self._create_id(),
            uid=uid,
            method=method,
            token_hash=_hash_token(token),
            attr_values=attr_values,
            opened_at=self._get_now(),
        )
        await self.project.auth.storage.sessions.open(session)
        return AuthSessionToken(session_id=session.id, token=token)

    @t.final
    async def authenticate(self, token: str) -> AuthCaller:
        """
        The caller of the session of a token: its uid, the id of the session and
        the permissions of the access, from the cache, or formed on a miss.

        :raises AuthSessionNotFoundError: no open session has the token.
        :raises AuthSessionExpiredError: its session expired, closed now.
        """
        token_hash = _hash_token(token)
        cache = self.project.auth.cache
        now = self._get_now()
        session = await cache.sessions.get(token_hash)
        if session is None:
            session = await self.project.auth.storage.sessions.find(token_hash)
            await cache.sessions.put(session, now + self._get_cache_ttl())
        reason = self.lifetime.check(session, now)
        if reason is not None:
            await self._expire(session, reason, now)
            raise AuthSessionExpiredError.for_reason(reason)
        access = self.project.auth.access
        groups_digest = access.groups.get_digest()
        caller = await cache.callers.get(token_hash, groups_digest)
        if caller is None:
            permissions = await access.permissions.get_permissions(session.uid)
            caller = AuthCaller(
                uid=session.uid, session_id=session.id, permissions=permissions
            )
            expires_at = now + self._get_cache_ttl()
            await cache.callers.put(token_hash, groups_digest, caller, expires_at)
        return caller

    @t.final
    async def forget_callers(self, uid: str) -> None:
        """
        Forgets the callers of the open sessions of a profile in the cache, the
        sessions kept: the next request of each forms its caller again, signed
        in still. Called once the storage keeps a change of what a caller
        holds, a membership of a group.
        """
        groups_digest = self.project.auth.access.groups.get_digest()
        callers = self.project.auth.cache.callers
        for session in await self.project.auth.storage.sessions.get_open(uid):
            await callers.forget(session.token_hash, groups_digest)

    def _create_id(self) -> str:
        """The id of a new session: random, as the uids are."""
        return os.urandom(16).hex()

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)

    def _get_cache_ttl(self) -> datetime.timedelta:
        configs = self.project.settings.configs
        return datetime.timedelta(seconds=configs.AUTH_SESSION_CACHE_TTL)

    async def _expire(
        self,
        session: AuthSessionRecord,
        reason: AuthSessionCloseReason,
        now: datetime.datetime,
    ) -> None:
        """Closes an expired session and forgets it in the cache."""
        try:
            await self.project.auth.storage.sessions.close(session.id, reason, now)
        except AuthSessionNotFoundError:
            pass  # closed meanwhile, by another request
        cache = self.project.auth.cache
        await cache.sessions.forget(session.token_hash)
        groups_digest = self.project.auth.access.groups.get_digest()
        await cache.callers.forget(session.token_hash, groups_digest)


def _hash_token(token: str) -> str:
    # sha256: the token is random, a slow hash would buy nothing
    return hashlib.sha256(token.encode()).hexdigest()
