"""
The sign-up over gRPC: its answers, of :mod:`ingot_auth.api`. Temporary: its
names suffixed ``Temp``, its services bound as ``*_temp`` beside the old
ones, till the old API is removed.
"""

__all__ = ("AuthGrpcSignUpServicerTemp", "build_sign_up_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcServicer

from ingot_auth.api import AuthSignUpRpcMixin
from ingot_auth.api.results import build_sign_up_result
from .base import Context, GrpcAuthRpcContext
from ingot_auth.api.sign_up.v1 import sign_up_pb2, sign_up_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignUpServicerTemp(
    AuthSignUpRpcMixin, GrpcServicer, sign_up_pb2_grpc.SignUpServicer
):
    """
    The answers, of :class:`~ingot_auth.api.AuthSignUpRpcMixin`,
    over gRPC.
    """

    project: "AuthProject"

    @t.override
    async def AnswerSignUp(
        self, request: sign_up_pb2.AnswerSignUpRequest, context: Context
    ) -> sign_up_pb2.AnswerSignUpResponse:
        return await self.rpc_answer_sign_up(request, GrpcAuthRpcContext(context))
