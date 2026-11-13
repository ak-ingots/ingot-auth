"""The sign-in over gRPC: the results of its steps, and its answers."""

__all__ = ("AuthGrpcSignInBinding", "AuthGrpcSignInServicer", "build_sign_in_result")

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

from ingot_auth.sign_in import (
    AuthAnswerSignInParameters,
    AuthSignedIn,
    AuthSignInResult,
)

from .base import Context
from .challenges import build_challenge
from ingot_auth.sign_in.v1 import sign_in_pb2, sign_in_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcSignInServicer(GrpcServicer, sign_in_pb2_grpc.SignInServicer):
    """
    The answers of a sign-in, by any method or factor, open to anyone, as
    every flow is, run for the anonymous caller of the project: whose
    challenge it is, the attempt knows.
    """

    project: "AuthProject"

    @t.override
    async def AnswerSignIn(
        self, request: sign_in_pb2.AnswerSignInRequest, context: Context
    ) -> sign_in_pb2.AnswerSignInResponse:
        # the one kind of an answer, a code: one not given is a wrong one
        parameters = AuthAnswerSignInParameters(
            attempt_id=request.attempt_id, answer=request.code
        )
        factory = self.project.auth.sign_in.op_answer
        result = await self.run_operation(factory, parameters, context)
        return sign_in_pb2.AnswerSignInResponse(result=build_sign_in_result(result))


class AuthGrpcSignInBinding:
    auth_sign_in = GrpcService(sign_in_pb2_grpc.SignInStub, AuthGrpcSignInServicer)


def build_sign_in_result(result: AuthSignInResult) -> sign_in_pb2.SignInResult:
    """Internal: the message of the result of a step of a sign-in."""
    if isinstance(result, AuthSignedIn):
        return sign_in_pb2.SignInResult(
            signed_in=sign_in_pb2.SignedIn(
                session_id=result.session_id, token=result.token
            )
        )
    return sign_in_pb2.SignInResult(
        challenge=build_challenge(result.attempt_id, result.challenge)
    )
