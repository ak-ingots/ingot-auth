"""The sign-up over gRPC: the results of its steps, and its answers."""

__all__ = ("AuthGrpcSignUpBinding", "AuthGrpcSignUpServicer", "build_sign_up_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

from ingot_auth.sign_up import (
    AuthAnswerSignUpParameters,
)

from .base import Context
from ..contract.results import build_sign_up_result
from ingot_auth.sign_up.v1 import sign_up_pb2, sign_up_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignUpServicer(GrpcServicer, sign_up_pb2_grpc.SignUpServicer):
    """
    The answers of a sign-up, by any method or factor, open to anyone, as
    every flow is, run for the anonymous caller of the project: whose
    challenge it is, the attempt knows.
    """

    project: "AuthProject"

    @t.override
    async def AnswerSignUp(
        self, request: sign_up_pb2.AnswerSignUpRequest, context: Context
    ) -> sign_up_pb2.AnswerSignUpResponse:
        # the one kind of an answer, a code: one not given is a wrong one
        parameters = AuthAnswerSignUpParameters(
            attempt_uid=request.attempt_uid, answer=request.code
        )
        factory = self.project.auth.sign_up.op_answer
        result = await self.run_operation(factory, parameters, context)
        return sign_up_pb2.AnswerSignUpResponse(result=build_sign_up_result(result))


class AuthGrpcSignUpBinding:
    auth_sign_up = GrpcService(sign_up_pb2_grpc.SignUpStub, AuthGrpcSignUpServicer)
