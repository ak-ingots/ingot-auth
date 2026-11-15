"""The sign-out over gRPC."""

__all__ = ("AuthGrpcSignOutBinding", "AuthGrpcSignOutServicer")

import typing as t

from ingot_grpcio.grpc.services import GrpcService
from ingots.defaults.operations import Caller

from ingot_auth.sessions import AuthSessionExpiredError
from ingot_auth.storages import AuthSessionNotFoundError

from .base import BaseAuthGrpcServicer, Context
from ingot_auth.sign_out.v1 import sign_out_pb2, sign_out_pb2_grpc


class AuthGrpcSignOutServicer(BaseAuthGrpcServicer, sign_out_pb2_grpc.SignOutServicer):
    """
    The sign-out of the caller of the token of a call, open to any caller: a
    token closed, expired or unknown gives the anonymous one, which signs out
    of nothing, so that a client may retry and learns nothing.
    """

    @t.override
    async def SignOut(
        self, request: sign_out_pb2.SignOutRequest, context: Context
    ) -> sign_out_pb2.SignOutResponse:
        factory = self.project.auth.sign_out.op_sign_out
        await self.run_operation(factory, None, context)
        return sign_out_pb2.SignOutResponse()

    @t.override
    async def _get_caller(self, context: Context) -> Caller:
        try:
            return await super()._get_caller(context)
        except AuthSessionNotFoundError, AuthSessionExpiredError:
            return self.project.operations.callers.get_anonymous()


class AuthGrpcSignOutBinding:
    auth_sign_out = GrpcService(sign_out_pb2_grpc.SignOutStub, AuthGrpcSignOutServicer)
