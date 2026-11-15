"""The sessions of the caller's own over gRPC."""

__all__ = ("AuthGrpcSessionsServicer",)

import typing as t

from ingot_auth.sessions import AuthOwnSession, AuthRevokeOwnSessionParameters

from ..base import BaseAuthGrpcServicer, Context
from .attrs import build_attr_value_message
from ingot_auth.sessions.v1 import sessions_pb2, sessions_pb2_grpc


class AuthGrpcSessionsServicer(
    BaseAuthGrpcServicer, sessions_pb2_grpc.SessionsServicer
):
    """The sessions of the caller of the token: its own, listed and revoked."""

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
