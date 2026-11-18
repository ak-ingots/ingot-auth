"""
The sessions: what a sign-in opens and a token stands for, the caller of a
request, with the registry of the attributes of what a sign-up, a sign-in
happened on and the presets asking for them, and the groups of the work of
these registries. Their storage is in
:mod:`ingot_auth.storages`, their caches in :mod:`ingot_auth.caches`.
"""

__all__ = (
    "AuthEvictOldestLimit",
    "AuthFixedLifetime",
    "AuthListOwnSessionsOperation",
    "AuthListSessionsCommand",
    "AuthListSessionsOperation",
    "AuthListSessionsParameters",
    "AuthNoLimit",
    "AuthNoSessionAttrsDeriver",
    "AuthOwnSessionNotFoundError",
    "AuthRefuseLimit",
    "AuthOwnSession",
    "AuthRevokeAllSessionsCommand",
    "AuthRevokeAllSessionsOperation",
    "AuthRevokeAllSessionsParameters",
    "AuthRevokeOtherSessionsOperation",
    "AuthRevokeOwnSessionOperation",
    "AuthRevokeOwnSessionParameters",
    "AuthSessionExpired",
    "AuthSessionExpiredError",
    "AuthSessionInfo",
    "AuthSessionsAdminsGroup",
    "AuthSessionsConsumersGroup",
    "AuthSessionsLimitError",
    "AuthSessionsManagersGroup",
    "AuthSlidingFixedLifetime",
    "AuthSlidingLifetime",
    "AuthSessionToken",
    "AuthSessionsUnit",
    "AuthSweepSessionsCommand",
    "AuthSweepSessionsOperation",
    "AuthSweepSessionsParameters",
    "BaseAuthSessionAttrsDeriver",
    "BaseAuthMaxSessionsLimit",
    "BaseAuthSessionLifetime",
    "BaseAuthSessionsLimit",
)

import dataclasses
import datetime
import hashlib
import logging
import os
import secrets
import typing as t

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    PermissionsSlot,
)
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access.groups import AuthGroupsOwner
from ingot_auth.caches import AuthCaller
from ingot_auth.profiles.hashes import build_profile_hash
from ingot_auth.storages import (
    AuthActivityAction,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
    AuthSessionRecord,
)

from .attrs import AuthSessionAttrsUnit
from .commands import (
    AuthListSessionsCommand,
    AuthRevokeAllSessionsCommand,
    AuthSweepSessionsCommand,
)
from .derivers import AuthNoSessionAttrsDeriver, BaseAuthSessionAttrsDeriver
from .errors import (
    AuthOwnSessionNotFoundError,
    AuthSessionExpiredError,
    AuthSessionsLimitError,
)
from .groups import (
    AuthSessionsAdminsGroup,
    AuthSessionsConsumersGroup,
    AuthSessionsManagersGroup,
)
from .data import AuthOwnSession, AuthSessionExpired, AuthSessionInfo, AuthSessionToken
from .lifetimes import (
    AuthFixedLifetime,
    AuthSlidingFixedLifetime,
    AuthSlidingLifetime,
    BaseAuthSessionLifetime,
)
from .limits import (
    AuthEvictOldestLimit,
    AuthNoLimit,
    AuthRefuseLimit,
    BaseAuthMaxSessionsLimit,
    BaseAuthSessionsLimit,
)
from .operations import (
    AuthListOwnSessionsOperation,
    AuthListSessionsOperation,
    AuthListSessionsParameters,
    AuthRevokeAllSessionsOperation,
    AuthRevokeAllSessionsParameters,
    AuthRevokeOtherSessionsOperation,
    AuthRevokeOwnSessionOperation,
    AuthRevokeOwnSessionParameters,
    AuthSweepSessionsOperation,
    AuthSweepSessionsParameters,
)
from .presets import AuthSessionPresetsUnit

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ingots.defaults.operations import OperationMetadata

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue


logger = logging.getLogger(__name__)


class AuthSessionsUnit(AuthGroupsOwner, OperationsOwner, CliUnit):
    """
    The sessions: the registries of their attributes and of the presets, the
    strategy of their lifetime in the slot ``lifetime``, the one deriving
    values of their attributes in the slot ``deriver`` and the one of their
    limit in the slot ``limit``, none by default, which a project declares. A
    sign-in makes room, :meth:`make_room`, opens a session and gives its token;
    a request brings the token, and :meth:`authenticate` turns it into the
    caller, from the cache, or from the storage and the access on a miss. A
    change of what a caller holds forgets the callers of the profile,
    :meth:`forget_callers`. The groups of the work of the registries:
    ``auth.sessions.grp_consumers``, who reads them, ``auth.sessions.grp_managers``,
    who keeps them, binding none, ``auth.sessions.grp_admins``, who binds too.
    A signed-in user lists its own open sessions and revokes them, one by one
    or all but the current one, by the flags ``auth.grp_signed_in`` grants;
    an operator reads those of a profile, the closed ones too, the record of
    its sign-ins, ``auth sessions list <uid> --closed``, and revokes them all,
    ``auth sessions revoke-all <profile_uid>``; an admin, or a job of a
    schedule as ``auth.system``, sweeps the expired ones, ``auth sessions sweep``.
    """

    class Flags(PermissionFlags):
        """
        The flags of the domain of the sessions, the full name of their unit,
        ``auth.sessions``: each kept for good, as the masks are stored and sent.
        ``auth.grp_signed_in`` grants a signed-in user its own,
        ``auth.sessions.grp_admins`` the listing of those of a profile, the
        record of its sign-ins, their revoking, and the sweep of the expired.
        """

        CAN_LIST_OWN = 1 << 0
        CAN_REVOKE_OWN = 1 << 1
        CAN_LIST = 1 << 2
        CAN_REVOKE = 1 << 3
        CAN_SWEEP = 1 << 4

    cli_name = "sessions"
    cli_description = "The sessions of the users."

    project: "AuthProject"

    grp_consumers = Slot(AuthSessionsConsumersGroup)
    grp_managers = Slot(AuthSessionsManagersGroup)
    grp_admins = Slot(AuthSessionsAdminsGroup)

    permissions = PermissionsSlot(Flags)

    op_list_own = Factory(AuthListOwnSessionsOperation)
    op_revoke_own = Factory(AuthRevokeOwnSessionOperation)
    op_revoke_others = Factory(AuthRevokeOtherSessionsOperation)
    op_list = Factory(AuthListSessionsOperation)
    op_revoke_all = Factory(AuthRevokeAllSessionsOperation)
    op_sweep = Factory(AuthSweepSessionsOperation)

    cmd_list = Slot(AuthListSessionsCommand)
    cmd_revoke_all = Slot(AuthRevokeAllSessionsCommand)
    cmd_sweep = Slot(AuthSweepSessionsCommand)

    attrs = Slot(AuthSessionAttrsUnit)
    presets = Slot(AuthSessionPresetsUnit)
    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    lifetime = Slot(BaseAuthSessionLifetime)  # type: ignore[type-abstract]
    deriver = Slot(BaseAuthSessionAttrsDeriver)  # type: ignore[type-abstract]
    limit = Slot(BaseAuthSessionsLimit)  # type: ignore[type-abstract]

    @t.final
    async def make_room(
        self, uid: str, metadata: "OperationMetadata"
    ) -> "tuple[AuthSessionRecord, ...]":
        """
        Makes room for a session of a profile by the strategy of the limit, in
        the transaction of the sign-in: gives the sessions it closed, which
        :meth:`forget_closed` forgets after the commit.

        :raises AuthSessionsLimitError: the strategy refuses the sign-in.
        """
        return await self.limit.make_room(uid, self._get_now(), metadata)

    @t.final
    async def forget_closed(self, sessions: "Iterable[AuthSessionRecord]") -> None:
        """Forgets sessions closed in the cache, once the storage keeps them so."""
        for session in sessions:
            await self._forget(session.token_hash)

    @t.final
    async def open(
        self, uid: str, method: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> AuthSessionToken:
        """
        Opens a session of a profile signed in by a method, with the values of
        the attributes of the session, checked by the caller, and gives its
        token, 256 random bits, given once, kept by none but the client, with
        the uid of the session.
        """
        token = secrets.token_urlsafe(32)
        now = self._get_now()
        session = AuthSessionRecord(
            uid=self._create_uid(),
            profile_uid=uid,
            method=method,
            token_hash=_hash_token(token),
            attr_values=attr_values,
            opened_at=now,
            seen_at=now,
        )
        await self.project.auth.storage.sessions.open(session)
        return AuthSessionToken(session_uid=session.uid, token=token)

    @t.final
    async def authenticate(self, token: str) -> AuthCaller:
        """
        The caller of the session of a token: its uid, the uid of the session and
        the permissions of the access, from the cache, or formed on a miss. The
        time the session is seen at is written as the strategy of its lifetime
        says.

        :raises AuthSessionNotFoundError: no open session has the token.
        :raises AuthSessionExpiredError: its session expired, closed now.
        """
        token_hash = _hash_token(token)
        cache = self.project.auth.cache
        now = self._get_now()
        session = await cache.sessions.get(token_hash)
        if session is None:
            session = await self._find(token_hash, now)
        elif self.lifetime.check(session, now) is not None:
            # the session cached may have been seen since, by another process
            session = await self._find(token_hash, now)
        reason = self.lifetime.check(session, now)
        if reason is not None:
            await self._expire(session, reason, now)
            raise AuthSessionExpiredError.for_reason(reason)
        if self.lifetime.is_touch_due(session, now):
            session = await self._touch(session, now)
        access = self.project.auth.access
        groups_digest = access.groups.get_digest()
        caller = await cache.callers.get(token_hash, groups_digest)
        if caller is None:
            permissions = await access.permissions.get_permissions(session.profile_uid)
            values = await self.project.auth.storage.profiles.values.get(
                session.profile_uid
            )
            caller = AuthCaller(
                uid=session.profile_uid,
                session_uid=session.uid,
                permissions=permissions,
                profile_hash=build_profile_hash(values, permissions),
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

    @t.final
    async def close(
        self,
        uid: str,
        session_uid: str,
        reason: AuthSessionCloseReason,
    ) -> None:
        """
        Closes an open session of a profile for a reason, kept, then forgets
        it in the cache, once the storage keeps it closed: the next request of
        its token misses the cache and finds it closed. Who closed it, the
        activity log tells.

        :raises AuthSessionNotFoundError: no open session of the profile has
            the id.
        """
        for session in await self.project.auth.storage.sessions.get_open(uid):
            if session.uid == session_uid:
                break
        else:
            raise AuthSessionNotFoundError.for_uid(session_uid)
        try:
            await self.project.auth.storage.sessions.close(
                session.uid, reason, self._get_now()
            )
        except AuthSessionNotFoundError:
            pass  # closed meanwhile, by another request
        await self._forget(session.token_hash)

    def _create_uid(self) -> str:
        """The id of a new session: random, as the uids are."""
        return os.urandom(16).hex()

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)

    def _get_cache_ttl(self) -> datetime.timedelta:
        configs = self.project.settings.configs
        return datetime.timedelta(seconds=configs.AUTH_SESSION_CACHE_TTL)

    async def _find(self, token_hash: str, now: datetime.datetime) -> AuthSessionRecord:
        """
        The open session of the hash of a token from the storage, kept in the
        cache; one not open is forgotten there.
        """
        try:
            session = await self.project.auth.storage.sessions.find(token_hash)
        except AuthSessionNotFoundError:
            await self._forget(token_hash)
            raise
        await self.project.auth.cache.sessions.put(session, now + self._get_cache_ttl())
        return session

    async def _touch(
        self, session: AuthSessionRecord, now: datetime.datetime
    ) -> AuthSessionRecord:
        """Writes the time a session is seen at, in the storage and the cache."""
        try:
            await self.project.auth.storage.sessions.touch(session.uid, now)
        except AuthSessionNotFoundError:
            await self._forget(session.token_hash)
            raise
        session = dataclasses.replace(session, seen_at=now)
        await self.project.auth.cache.sessions.put(session, now + self._get_cache_ttl())
        return session

    async def _expire(
        self,
        session: AuthSessionRecord,
        reason: AuthSessionCloseReason,
        now: datetime.datetime,
    ) -> None:
        """
        Closes an expired session and forgets it in the cache, recorded in the
        activity log by the server itself, ``auth.system``, in a run of its
        own, which the line of the log tells, to link them.
        """
        auth = self.project.auth
        operations = self.project.operations
        metadata = operations.create_metadata(operations.callers.get_auth_system())
        logger.info(
            "the session %s expired, %s, run %s", session.uid, reason, metadata.run_uid
        )
        try:
            async with auth.storage.transaction():
                await auth.storage.sessions.close(session.uid, reason, now)
                await auth.activities.record(
                    self,
                    session.uid,
                    AuthActivityAction.EXPIRE,
                    metadata,
                    context=AuthSessionExpired(reason=reason.value),
                )
        except AuthSessionNotFoundError:
            pass  # closed meanwhile, by another request
        await self._forget(session.token_hash)

    async def _forget(self, token_hash: str) -> None:
        """Forgets the session of the hash of a token and its caller in the cache."""
        cache = self.project.auth.cache
        await cache.sessions.forget(token_hash)
        groups_digest = self.project.auth.access.groups.get_digest()
        await cache.callers.forget(token_hash, groups_digest)


def _hash_token(token: str) -> str:
    # sha256: the token is random, a slow hash would buy nothing
    return hashlib.sha256(token.encode()).hexdigest()
