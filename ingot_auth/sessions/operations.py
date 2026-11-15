"""The operations of the sessions: of the caller's own, of a profile."""

__all__ = (
    "AuthListOwnSessionsOperation",
    "AuthListSessionsOperation",
    "AuthRevokeOtherSessionsOperation",
    "AuthRevokeOwnSessionOperation",
)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.caches import AuthCaller
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionNotFoundError

from .errors import AuthOwnSessionNotFoundError
from .items import (
    AuthListSessionsParameters,
    AuthOwnSession,
    AuthRevokeOwnSessionParameters,
    AuthSessionInfo,
)

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

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
                id=session.id,
                attr_values=session.attr_values,
                opened_at=session.opened_at,
                seen_at=session.seen_at,
                is_current=session.id == caller.session_id,
            )
            for session in await self.project.auth.storage.sessions.get_open(caller.uid)
        )


class AuthRevokeOwnSessionOperation(
    BaseOperation[AuthRevokeOwnSessionParameters, None]
):
    """
    Closes an open session of the caller's own, ``REVOKED``, a lost phone, the
    current one too.

    :raises AuthOwnSessionNotFoundError: no open session of the caller has the
        id: one of another is not found either.
    """

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
            raise AuthOwnSessionNotFoundError.for_id(parameters.session_id)
        try:
            await self.parent.close(
                caller.uid,
                parameters.session_id,
                AuthSessionCloseReason.REVOKED,
                closed_by=caller.uid,
            )
        except AuthSessionNotFoundError:
            raise AuthOwnSessionNotFoundError.for_id(parameters.session_id) from None


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
            if session.id == caller.session_id:
                continue
            try:
                await self.parent.close(
                    caller.uid,
                    session.id,
                    AuthSessionCloseReason.REVOKED,
                    closed_by=caller.uid,
                )
            except AuthSessionNotFoundError:
                continue  # closed meanwhile, by another request
            closed += 1
        return closed


class AuthListSessionsOperation(
    BaseOperation[AuthListSessionsParameters, tuple[AuthSessionInfo, ...]]
):
    """
    The sessions of a profile, by the time they opened: those open, or all of
    them, the closed ones with when, why and by whom, the record of its
    sign-ins. An operator reads it, not the user.
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
            sessions = await storage.get_all(parameters.uid)
        else:
            sessions = await storage.get_open(parameters.uid)
        return tuple(
            AuthSessionInfo(
                id=session.id,
                uid=session.uid,
                method=session.method,
                attr_values=session.attr_values,
                opened_at=session.opened_at,
                seen_at=session.seen_at,
                closed_at=session.closed_at,
                close_reason=session.close_reason,
                closed_by=session.closed_by,
            )
            for session in sessions
        )
