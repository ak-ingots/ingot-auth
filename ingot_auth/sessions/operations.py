"""The operations of the sessions: of the caller's own, of a profile."""

__all__ = (
    "AuthListOwnSessionsOperation",
    "AuthListSessionsOperation",
    "AuthListSessionsParameters",
    "AuthRevokeAllSessionsOperation",
    "AuthRevokeAllSessionsParameters",
    "AuthRevokeOtherSessionsOperation",
    "AuthRevokeOwnSessionOperation",
    "AuthRevokeOwnSessionParameters",
    "AuthSweepSessionsOperation",
    "AuthSweepSessionsParameters",
)

import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.caches import AuthCaller
from ingot_auth.storages import (
    AuthActivityAction,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)

from .errors import AuthOwnSessionNotFoundError
from .data import AuthOwnSession, AuthSessionExpired, AuthSessionInfo

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthSessionRecord

    from . import AuthSessionsUnit


class AuthListOwnSessionsOperation(BaseOperation[None, tuple[AuthOwnSession, ...]]):
    """
    The open sessions of the caller, by the time they opened, the current one
    marked; none of a caller of no session, the root.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_LIST_OWN)

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[AuthOwnSession, ...]:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            return ()
        return tuple(
            AuthOwnSession(
                uid=session.uid,
                attr_values=session.attr_values,
                opened_at=session.opened_at,
                seen_at=session.seen_at,
                is_current=session.uid == caller.session_uid,
            )
            for session in _by_opening(
                await self.project.auth.storage.sessions.get_open(caller.uid)
            )
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRevokeOwnSessionParameters:
    """The public uid of a session of the caller's own."""

    session_uid: str


class AuthRevokeOwnSessionOperation(
    BaseOperation[AuthRevokeOwnSessionParameters, None]
):
    """
    Closes an open session of the caller's own, ``REVOKED``, a lost phone, the
    current one too.

    :raises AuthOwnSessionNotFoundError: no open session of the caller has the
        id: one of another is not found either.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_REVOKE_OWN)

    @t.override
    async def _run(
        self, parameters: AuthRevokeOwnSessionParameters, metadata: OperationMetadata
    ) -> None:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            raise AuthOwnSessionNotFoundError.for_uid(parameters.session_uid)
        auth = self.project.auth
        try:
            async with auth.storage.transaction():
                await self.parent.close(
                    caller.uid,
                    parameters.session_uid,
                    AuthSessionCloseReason.REVOKED,
                )
                await auth.activities.record(
                    self.parent,
                    parameters.session_uid,
                    AuthActivityAction.REVOKE,
                    metadata,
                )
        except AuthSessionNotFoundError:
            raise AuthOwnSessionNotFoundError.for_uid(parameters.session_uid) from None


class AuthRevokeOtherSessionsOperation(BaseOperation[None, int]):
    """
    Closes the open sessions of the caller but the current one, ``REVOKED``,
    and tells how many; none of a caller of no session, the root.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_REVOKE_OWN)

    @t.override
    async def _run(self, parameters: None, metadata: OperationMetadata) -> int:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            return 0
        closed = 0
        for session in await self.project.auth.storage.sessions.get_open(caller.uid):
            if session.uid == caller.session_uid:
                continue
            try:
                async with self.project.auth.storage.transaction():
                    await self.parent.close(
                        caller.uid,
                        session.uid,
                        AuthSessionCloseReason.REVOKED,
                    )
                    await self.project.auth.activities.record(
                        self.parent, session.uid, AuthActivityAction.REVOKE, metadata
                    )
            except AuthSessionNotFoundError:
                continue  # closed meanwhile, by another request
            closed += 1
        return closed


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRevokeAllSessionsParameters:
    """The uid of a profile, whose open sessions are all revoked."""

    profile_uid: str


class AuthRevokeAllSessionsOperation(
    BaseOperation[AuthRevokeAllSessionsParameters, int]
):
    """
    Closes every open session of a profile, ``REVOKED``, a stolen account, and
    tells how many; none of an unknown profile. An operator runs it.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_REVOKE)

    @t.override
    async def _run(
        self, parameters: AuthRevokeAllSessionsParameters, metadata: OperationMetadata
    ) -> int:
        profile_uid = parameters.profile_uid
        closed = 0
        for session in await self.project.auth.storage.sessions.get_open(profile_uid):
            try:
                async with self.project.auth.storage.transaction():
                    await self.parent.close(
                        profile_uid, session.uid, AuthSessionCloseReason.REVOKED
                    )
                    await self.project.auth.activities.record(
                        self.parent, session.uid, AuthActivityAction.REVOKE, metadata
                    )
            except AuthSessionNotFoundError:
                continue  # closed meanwhile, by another request
            closed += 1
        return closed


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSweepSessionsParameters:
    """How many open sessions a sweep reads a page, closed in a transaction."""

    page_size: int = 1000


class AuthSweepSessionsOperation(BaseOperation[AuthSweepSessionsParameters, int]):
    """
    Closes every open session the strategy of the lifetime tells expired, with
    its reason, as :meth:`AuthSessionsUnit.authenticate` closes one, and tells
    how many: a page of the storage at a time, each in a transaction of its
    own, so that a sweep stopped halfway keeps what it closed. Its caller is
    in the log, an admin, or ``auth.system``, a job of a schedule.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_SWEEP)

    @t.override
    async def _run(
        self, parameters: AuthSweepSessionsParameters, metadata: OperationMetadata
    ) -> int:
        auth = self.project.auth
        now = self.parent._get_now()
        closed = 0
        after: str | None = None
        while page := await auth.storage.sessions.get_all_open(
            after, parameters.page_size
        ):
            after = page[-1].uid
            expired = []
            async with auth.storage.transaction():
                for session in page:
                    reason = self.parent.lifetime.check(session, now)
                    if reason is None:
                        continue
                    try:
                        await auth.storage.sessions.close(session.uid, reason, now)
                    except AuthSessionNotFoundError:
                        continue  # closed meanwhile, by another request
                    await auth.activities.record(
                        self.parent,
                        session.uid,
                        AuthActivityAction.EXPIRE,
                        metadata,
                        context=AuthSessionExpired(reason=reason.value),
                    )
                    expired.append(session)
            for session in expired:  # once the storage keeps them closed
                await self.parent._forget(session.token_hash)
            closed += len(expired)
        return closed


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthListSessionsParameters:
    """The uid of a profile; its closed sessions too, the record, if told."""

    profile_uid: str
    closed: bool = False


class AuthListSessionsOperation(
    BaseOperation[AuthListSessionsParameters, tuple[AuthSessionInfo, ...]]
):
    """
    The sessions of a profile, by the time they opened: those open, or all of
    them, the closed ones with when and why, the record of its sign-ins. An
    operator reads it, not the user.
    """

    project: "AuthProject"
    parent: "AuthSessionsUnit"

    @t.override
    def _get_permissions(self) -> Permissions:
        permissions = self.parent.permissions
        return permissions(permissions.flags.CAN_LIST)

    @t.override
    async def _run(
        self, parameters: AuthListSessionsParameters, metadata: OperationMetadata
    ) -> tuple[AuthSessionInfo, ...]:
        storage = self.project.auth.storage.sessions
        if parameters.closed:
            sessions = await storage.get_all(parameters.profile_uid)
        else:
            sessions = _by_opening(await storage.get_open(parameters.profile_uid))
        return tuple(
            AuthSessionInfo(
                uid=session.uid,
                profile_uid=session.profile_uid,
                method=session.method,
                attr_values=session.attr_values,
                opened_at=session.opened_at,
                seen_at=session.seen_at,
                closed_at=session.closed_at,
                close_reason=session.close_reason,
            )
            for session in sessions
        )


def _by_opening(
    sessions: "Iterable[AuthSessionRecord]",
) -> "tuple[AuthSessionRecord, ...]":
    """The sessions by the time they opened, as a list shows them."""
    return tuple(sorted(sessions, key=lambda session: (session.opened_at, session.uid)))
