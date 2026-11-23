"""The sign-out over gRPC."""

__all__ = ("AuthGrpcSignOutBinding", "AuthGrpcSignOutServicer")

import typing as t

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api import AuthSignOutRpcMixin
from .base import BaseAuthGrpcServicer, Context, GrpcAuthRpcContext
from ingot_auth.api.sign_out.v1 import sign_out_pb2, sign_out_pb2_grpc


class AuthGrpcSignOutServicer(
    AuthSignOutRpcMixin, BaseAuthGrpcServicer, sign_out_pb2_grpc.SignOutServicer
):
    """
    The sign-out, of
    :class:`~ingot_auth.api.AuthSignOutRpcMixin`, over gRPC.
    """

    @t.override
    async def SignOut(
        self, request: sign_out_pb2.SignOutRequest, context: Context
    ) -> sign_out_pb2.SignOutResponse:
        return await self.rpc_sign_out(request, GrpcAuthRpcContext(context))


class AuthGrpcSignOutBinding:
    auth_sign_out = GrpcService(sign_out_pb2_grpc.SignOutStub, AuthGrpcSignOutServicer)
