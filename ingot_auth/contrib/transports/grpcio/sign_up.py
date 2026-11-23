"""The sign-up over gRPC: its answers."""

__all__ = ("AuthGrpcSignUpBinding", "AuthGrpcSignUpServicer", "build_sign_up_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

from ingot_auth.api import AuthSignUpRpcMixin
from ingot_auth.api.results import build_sign_up_result
from .base import Context, GrpcAuthRpcContext
from ingot_auth.api.sign_up.v1 import sign_up_pb2, sign_up_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignUpServicer(
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


class AuthGrpcSignUpBinding:
    auth_sign_up = GrpcService(sign_up_pb2_grpc.SignUpStub, AuthGrpcSignUpServicer)
