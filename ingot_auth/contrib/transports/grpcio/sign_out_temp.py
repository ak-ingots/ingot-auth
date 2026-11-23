"""
The sign-out over gRPC, of :mod:`ingot_auth.api`. Temporary: its names
suffixed ``Temp``, its services bound as ``*_temp`` beside the old ones,
till the old API is removed.
"""

__all__ = ("AuthGrpcSignOutServicerTemp",)

import typing as t


from ingot_auth.api import AuthSignOutRpcMixin
from .base import BaseAuthGrpcServicer, Context, GrpcAuthRpcContext
from ingot_auth.api.sign_out.v1 import sign_out_pb2, sign_out_pb2_grpc


class AuthGrpcSignOutServicerTemp(
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
