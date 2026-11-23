"""The answers of the sign-up as messages, of no transport."""

__all__ = ("AuthSignUpRpcMixin",)

import typing as t

from ingot_auth.sign_up import AuthAnswerSignUpParameters

from ..base import AuthRpcMixin
from ..results import build_sign_up_result
from .v1 import sign_up_pb2

if t.TYPE_CHECKING:
    from ..context import BaseAuthRpcContext


class AuthSignUpRpcMixin(AuthRpcMixin):
    """
    The answers of a sign-up, by any method or factor, open to anyone, as
    every flow is, run for the anonymous caller of the project: whose
    challenge it is, the attempt knows.
    """

    @t.final
    async def rpc_answer_sign_up(
        self, request: sign_up_pb2.AnswerSignUpRequest, context: "BaseAuthRpcContext"
    ) -> sign_up_pb2.AnswerSignUpResponse:
        # the one kind of an answer, a code: one not given is a wrong one
        parameters = AuthAnswerSignUpParameters(
            attempt_uid=request.attempt_uid, answer=request.code
        )
        factory = self.project.auth.sign_up.op_answer
        result = await self.rpc_run_operation(factory, parameters, context)
        return sign_up_pb2.AnswerSignUpResponse(result=build_sign_up_result(result))
