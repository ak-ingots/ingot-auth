"""The servicer of the password of the profile of the caller."""

__all__ = ("AuthGrpcPasswordServicer",)

import typing as t

from ingot_auth.api import AuthPasswordRpcMixin
from ..base import BaseAuthGrpcServicer, Context, GrpcAuthRpcContext
from ingot_auth.api.methods.password.v1 import password_pb2, password_pb2_grpc


class AuthGrpcPasswordServicer(
    AuthPasswordRpcMixin, BaseAuthGrpcServicer, password_pb2_grpc.PasswordServicer
):
    """
    The change of the password of the caller, of
    :class:`~ingot_auth.api.AuthPasswordRpcMixin`, over gRPC.
    """

    @t.override
    async def ChangePassword(
        self, request: password_pb2.ChangePasswordRequest, context: Context
    ) -> password_pb2.ChangePasswordResponse:
        return await self.rpc_change_password(request, GrpcAuthRpcContext(context))
