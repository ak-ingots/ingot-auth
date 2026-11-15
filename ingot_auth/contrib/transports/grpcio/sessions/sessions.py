"""The sessions over gRPC: of the caller's own, of a profile."""

__all__ = ("AuthGrpcSessionsServicer",)

import typing as t

from ingot_auth.sessions import (
    AuthListSessionsParameters,
    AuthOwnSession,
    AuthRevokeOwnSessionParameters,
    AuthSessionInfo,
)
from ingot_auth.storages import AuthSessionCloseReason

from ..base import BaseAuthGrpcServicer, Context
from ..attrs import build_attr_value_message
from ingot_auth.sessions.v1 import sessions_pb2, sessions_pb2_grpc

CLOSE_REASONS: t.Final[
    dict[AuthSessionCloseReason, sessions_pb2.CloseReason.ValueType]
] = {
    AuthSessionCloseReason.SIGNED_OUT: sessions_pb2.CLOSE_REASON_SIGNED_OUT,
    AuthSessionCloseReason.REVOKED: sessions_pb2.CLOSE_REASON_REVOKED,
    AuthSessionCloseReason.EVICTED: sessions_pb2.CLOSE_REASON_EVICTED,
    AuthSessionCloseReason.EXPIRED_IDLE: sessions_pb2.CLOSE_REASON_EXPIRED_IDLE,
    AuthSessionCloseReason.EXPIRED_ABSOLUTE: sessions_pb2.CLOSE_REASON_EXPIRED_ABSOLUTE,
}


class AuthGrpcSessionsServicer(
    BaseAuthGrpcServicer, sessions_pb2_grpc.SessionsServicer
):
    """
    The sessions of the caller of the token: its own, listed and revoked; those
    of a profile, the record of its sign-ins, for an operator.
    """

    @t.override
    async def ListOwnSessions(
        self, request: sessions_pb2.ListOwnSessionsRequest, context: Context
    ) -> sessions_pb2.ListOwnSessionsResponse:
        factory = self.project.auth.sessions.op_list_own
        sessions = await self.run_operation(factory, None, context)
        return sessions_pb2.ListOwnSessionsResponse(
            sessions=[build_session_message(session) for session in sessions]
        )

    @t.override
    async def RevokeOwnSession(
        self, request: sessions_pb2.RevokeOwnSessionRequest, context: Context
    ) -> sessions_pb2.RevokeOwnSessionResponse:
        parameters = AuthRevokeOwnSessionParameters(session_id=request.session_id)
        factory = self.project.auth.sessions.op_revoke_own
        await self.run_operation(factory, parameters, context)
        return sessions_pb2.RevokeOwnSessionResponse()

    @t.override
    async def RevokeOtherSessions(
        self, request: sessions_pb2.RevokeOtherSessionsRequest, context: Context
    ) -> sessions_pb2.RevokeOtherSessionsResponse:
        factory = self.project.auth.sessions.op_revoke_others
        count = await self.run_operation(factory, None, context)
        return sessions_pb2.RevokeOtherSessionsResponse(count=count)

    @t.override
    async def ListSessions(
        self, request: sessions_pb2.ListSessionsRequest, context: Context
    ) -> sessions_pb2.ListSessionsResponse:
        parameters = AuthListSessionsParameters(uid=request.uid, closed=request.closed)
        factory = self.project.auth.sessions.op_list
        sessions = await self.run_operation(factory, parameters, context)
        return sessions_pb2.ListSessionsResponse(
            sessions=[build_session_record_message(session) for session in sessions]
        )


def build_session_message(session: AuthOwnSession) -> sessions_pb2.Session:
    """Internal: the message of an open session of the caller's own."""
    message = sessions_pb2.Session(
        id=session.id,
        attr_values=[
            build_attr_value_message(attr_id, value)
            for attr_id, value in session.attr_values.items()
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
        id=session.id,
        uid=session.uid,
        method=session.method,
        attr_values=[
            build_attr_value_message(attr_id, value)
            for attr_id, value in session.attr_values.items()
        ],
    )
    message.opened_at.FromDatetime(session.opened_at)
    message.seen_at.FromDatetime(session.seen_at)
    if session.closed_at is not None:
        message.closed_at.FromDatetime(session.closed_at)
    if session.close_reason is not None:
        message.close_reason = CLOSE_REASONS[session.close_reason]
    return message
