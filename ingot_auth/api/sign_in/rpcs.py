"""The answers of the sign-in as messages, of no transport."""

__all__ = ("AuthSignInRpcMixin",)

import typing as t

from ingot_auth.sign_in import AuthAnswerSignInParameters

from ..base import AuthRpcMixin
from ..results import build_sign_in_result
from .v1 import sign_in_pb2

if t.TYPE_CHECKING:
    from ..context import BaseAuthRpcContext


class AuthSignInRpcMixin(AuthRpcMixin):
    """
    The answers of a sign-in, by any method or factor, open to anyone, as
    every flow is, run for the anonymous caller of the project: whose
    challenge it is, the attempt knows.
    """

    @t.final
    async def rpc_answer_sign_in(
        self, request: sign_in_pb2.AnswerSignInRequest, context: "BaseAuthRpcContext"
    ) -> sign_in_pb2.AnswerSignInResponse:
        # the one kind of an answer, a code: one not given is a wrong one
        parameters = AuthAnswerSignInParameters(
            attempt_uid=request.attempt_uid, answer=request.code
        )
        factory = self.project.auth.sign_in.op_answer
        result = await self.rpc_run_operation(factory, parameters, context)
        return sign_in_pb2.AnswerSignInResponse(result=build_sign_in_result(result))
