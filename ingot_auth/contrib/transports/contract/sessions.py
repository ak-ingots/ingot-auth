"""The sessions as messages: the RPCs of their service, of no transport."""

__all__ = (
    "CLOSE_REASONS",
    "AuthSessionsRpcMixin",
    "build_session_message",
    "build_session_record_message",
)

import typing as t

from ingot_auth.sessions import (
    AuthListSessionsParameters,
    AuthOwnSession,
    AuthRevokeAllSessionsParameters,
    AuthRevokeOwnSessionParameters,
    AuthSessionInfo,
    AuthSweepSessionsParameters,
)
from ingot_auth.storages import AuthSessionCloseReason

from .attrs import build_attr_value_message
from .base import AuthSessionRpcMixin
from ingot_auth.sessions.v1 import sessions_pb2

if t.TYPE_CHECKING:
    from .context import BaseAuthRpcContext

#: The reason a session closed as the contract names it, each of the domain.
CLOSE_REASONS: t.Final[
    dict[AuthSessionCloseReason, sessions_pb2.CloseReason.ValueType]
] = {
    AuthSessionCloseReason.SIGNED_OUT: sessions_pb2.CLOSE_REASON_SIGNED_OUT,
    AuthSessionCloseReason.REVOKED: sessions_pb2.CLOSE_REASON_REVOKED,
    AuthSessionCloseReason.EVICTED: sessions_pb2.CLOSE_REASON_EVICTED,
    AuthSessionCloseReason.EXPIRED_IDLE: sessions_pb2.CLOSE_REASON_EXPIRED_IDLE,
    AuthSessionCloseReason.EXPIRED_ABSOLUTE: sessions_pb2.CLOSE_REASON_EXPIRED_ABSOLUTE,
}


class AuthSessionsRpcMixin(AuthSessionRpcMixin):
    """
    The sessions of the caller of the token: its own, listed and revoked; those
    of a profile, the record of its sign-ins, revoked all, for an operator.
    """

    @t.final
    async def rpc_list_own_sessions(
        self,
        request: sessions_pb2.ListOwnSessionsRequest,
        context: "BaseAuthRpcContext",
    ) -> sessions_pb2.ListOwnSessionsResponse:
        factory = self.project.auth.sessions.op_list_own
        sessions = await self.rpc_run_operation(factory, None, context)
        return sessions_pb2.ListOwnSessionsResponse(
            sessions=[build_session_message(session) for session in sessions]
        )

    @t.final
    async def rpc_revoke_own_session(
        self,
        request: sessions_pb2.RevokeOwnSessionRequest,
        context: "BaseAuthRpcContext",
    ) -> sessions_pb2.RevokeOwnSessionResponse:
        parameters = AuthRevokeOwnSessionParameters(session_uid=request.session_uid)
        factory = self.project.auth.sessions.op_revoke_own
        await self.rpc_run_operation(factory, parameters, context)
        return sessions_pb2.RevokeOwnSessionResponse()

    @t.final
    async def rpc_revoke_other_sessions(
        self,
        request: sessions_pb2.RevokeOtherSessionsRequest,
        context: "BaseAuthRpcContext",
    ) -> sessions_pb2.RevokeOtherSessionsResponse:
        factory = self.project.auth.sessions.op_revoke_others
        count = await self.rpc_run_operation(factory, None, context)
        return sessions_pb2.RevokeOtherSessionsResponse(count=count)

    @t.final
    async def rpc_list_sessions(
        self, request: sessions_pb2.ListSessionsRequest, context: "BaseAuthRpcContext"
    ) -> sessions_pb2.ListSessionsResponse:
        parameters = AuthListSessionsParameters(
            profile_uid=request.profile_uid, closed=request.closed
        )
        factory = self.project.auth.sessions.op_list
        sessions = await self.rpc_run_operation(factory, parameters, context)
        return sessions_pb2.ListSessionsResponse(
            sessions=[build_session_record_message(session) for session in sessions]
        )

    @t.final
    async def rpc_revoke_sessions(
        self, request: sessions_pb2.RevokeSessionsRequest, context: "BaseAuthRpcContext"
    ) -> sessions_pb2.RevokeSessionsResponse:
        parameters = AuthRevokeAllSessionsParameters(profile_uid=request.profile_uid)
        factory = self.project.auth.sessions.op_revoke_all
        count = await self.rpc_run_operation(factory, parameters, context)
        return sessions_pb2.RevokeSessionsResponse(count=count)

    @t.final
    async def rpc_sweep_sessions(
        self, request: sessions_pb2.SweepSessionsRequest, context: "BaseAuthRpcContext"
    ) -> sessions_pb2.SweepSessionsResponse:
        factory = self.project.auth.sessions.op_sweep
        count = await self.rpc_run_operation(
            factory, AuthSweepSessionsParameters(), context
        )
        return sessions_pb2.SweepSessionsResponse(count=count)


def build_session_message(session: AuthOwnSession) -> sessions_pb2.Session:
    """Internal: the message of an open session of the caller's own."""
    message = sessions_pb2.Session(
        uid=session.uid,
        attr_values=[
            build_attr_value_message(attr_uid, value)
            for attr_uid, value in session.attr_values.items()
        ],
        is_current=session.is_current,
    )
    message.opened_at.FromDatetime(session.opened_at)
    message.seen_at.FromDatetime(session.seen_at)
    return message


def build_session_record_message(
    session: AuthSessionInfo,
) -> sessions_pb2.SessionRecord:
    """Internal: the message of a session of a profile, open or closed."""
    message = sessions_pb2.SessionRecord(
        uid=session.uid,
        profile_uid=session.profile_uid,
        method=session.method,
        attr_values=[
            build_attr_value_message(attr_uid, value)
            for attr_uid, value in session.attr_values.items()
        ],
    )
    message.opened_at.FromDatetime(session.opened_at)
    message.seen_at.FromDatetime(session.seen_at)
    if session.closed_at is not None:
        message.closed_at.FromDatetime(session.closed_at)
    if session.close_reason is not None:
        message.close_reason = CLOSE_REASONS[session.close_reason]
    return message
