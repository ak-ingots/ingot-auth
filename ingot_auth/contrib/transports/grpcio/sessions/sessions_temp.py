"""
The sessions over gRPC: of the caller's own, of a profile, of
:mod:`ingot_auth.api`. Temporary: its names suffixed ``Temp``, its services
bound as ``*_temp`` beside the old ones, till the old API is removed.
"""

__all__ = ("CLOSE_REASONS", "AuthGrpcSessionsServicerTemp")

import typing as t

from ingot_auth.api import AuthSessionsRpcMixin
from ingot_auth.api.sessions.rpcs import CLOSE_REASONS
from ..base import BaseAuthGrpcServicer, Context, GrpcAuthRpcContext
from ingot_auth.api.sessions.v1 import sessions_pb2, sessions_pb2_grpc


class AuthGrpcSessionsServicerTemp(
    AuthSessionsRpcMixin, BaseAuthGrpcServicer, sessions_pb2_grpc.SessionsServicer
):
    """
    The sessions, of
    :class:`~ingot_auth.api.AuthSessionsRpcMixin`, over gRPC.
    """

    @t.override
    async def ListOwnSessions(
        self, request: sessions_pb2.ListOwnSessionsRequest, context: Context
    ) -> sessions_pb2.ListOwnSessionsResponse:
        return await self.rpc_list_own_sessions(request, GrpcAuthRpcContext(context))

    @t.override
    async def RevokeOwnSession(
        self, request: sessions_pb2.RevokeOwnSessionRequest, context: Context
    ) -> sessions_pb2.RevokeOwnSessionResponse:
        return await self.rpc_revoke_own_session(request, GrpcAuthRpcContext(context))

    @t.override
    async def RevokeOtherSessions(
        self, request: sessions_pb2.RevokeOtherSessionsRequest, context: Context
    ) -> sessions_pb2.RevokeOtherSessionsResponse:
        return await self.rpc_revoke_other_sessions(
            request, GrpcAuthRpcContext(context)
        )

    @t.override
    async def ListSessions(
        self, request: sessions_pb2.ListSessionsRequest, context: Context
    ) -> sessions_pb2.ListSessionsResponse:
        return await self.rpc_list_sessions(request, GrpcAuthRpcContext(context))

    @t.override
    async def RevokeSessions(
        self, request: sessions_pb2.RevokeSessionsRequest, context: Context
    ) -> sessions_pb2.RevokeSessionsResponse:
        return await self.rpc_revoke_sessions(request, GrpcAuthRpcContext(context))

    @t.override
    async def SweepSessions(
        self, request: sessions_pb2.SweepSessionsRequest, context: Context
    ) -> sessions_pb2.SweepSessionsResponse:
        return await self.rpc_sweep_sessions(request, GrpcAuthRpcContext(context))
