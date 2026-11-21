"""The sign-in over gRPC: its answers."""

__all__ = ("AuthGrpcSignInBinding", "AuthGrpcSignInServicer", "build_sign_in_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

from ..contract import AuthSignInRpcMixin
from ..contract.results import build_sign_in_result
from .base import Context, GrpcAuthRpcContext
from ingot_auth.sign_in.v1 import sign_in_pb2, sign_in_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignInServicer(
    AuthSignInRpcMixin, GrpcServicer, sign_in_pb2_grpc.SignInServicer
):
    """
    The answers, of :class:`~ingot_auth.contrib.transports.contract.AuthSignInRpcMixin`,
    over gRPC.
    """

    project: "AuthProject"

    @t.override
    async def AnswerSignIn(
        self, request: sign_in_pb2.AnswerSignInRequest, context: Context
    ) -> sign_in_pb2.AnswerSignInResponse:
        return await self.rpc_answer_sign_in(request, GrpcAuthRpcContext(context))


class AuthGrpcSignInBinding:
    auth_sign_in = GrpcService(sign_in_pb2_grpc.SignInStub, AuthGrpcSignInServicer)
