"""
The sign-in over gRPC: its answers, of :mod:`ingot_auth.api`. Temporary: its
names suffixed ``Temp``, its services bound as ``*_temp`` beside the old
ones, till the old API is removed.
"""

__all__ = ("AuthGrpcSignInServicerTemp", "build_sign_in_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcServicer

from ingot_auth.api import AuthSignInRpcMixin
from ingot_auth.api.results import build_sign_in_result
from .base import Context, GrpcAuthRpcContext
from ingot_auth.api.sign_in.v1 import sign_in_pb2, sign_in_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignInServicerTemp(
    AuthSignInRpcMixin, GrpcServicer, sign_in_pb2_grpc.SignInServicer
):
    """
    The answers, of :class:`~ingot_auth.api.AuthSignInRpcMixin`,
    over gRPC.
    """

    project: "AuthProject"

    @t.override
    async def AnswerSignIn(
        self, request: sign_in_pb2.AnswerSignInRequest, context: Context
    ) -> sign_in_pb2.AnswerSignInResponse:
        return await self.rpc_answer_sign_in(request, GrpcAuthRpcContext(context))
