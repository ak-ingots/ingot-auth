"""The RPCs of the method of an email and a code sent to it."""

__all__ = ("AuthEmailCodeRpcMixin",)

import typing as t

from ingot_auth.methods.email_code import AuthEmailCodeStart
from ingot_auth.sign_in import AuthStartSignInParameters
from ingot_auth.sign_up import AuthStartSignUpParameters

from ..attrs import SESSION_ATTRS, build_attr_values
from ..results import build_sign_in_result, build_sign_up_result
from .base import BaseAuthMethodRpcMixin
from ingot_auth.methods.email_code.v1 import email_code_pb2

if t.TYPE_CHECKING:
    from ..context import BaseAuthRpcContext


class AuthEmailCodeRpcMixin(BaseAuthMethodRpcMixin):
    """
    The starts of the method of an email and a code, of the method in the
    slot ``email_code``: each asks for the code, which the client gives by
    the answer of the flow.
    """

    METHOD: t.ClassVar[str] = "email_code"

    @t.final
    async def rpc_start_sign_up(
        self, request: email_code_pb2.StartSignUpRequest, context: "BaseAuthRpcContext"
    ) -> email_code_pb2.StartSignUpResponse:
        parameters = AuthStartSignUpParameters(
            method=self.METHOD,
            parameters=AuthEmailCodeStart(email=request.email),
            attr_values=build_attr_values(request.attr_values, SESSION_ATTRS),
            transport_attr_values=context.get_transport_attr_values(),
        )
        factory = self.project.auth.sign_up.op_start
        result = await self.rpc_run_operation(factory, parameters, context)
        return email_code_pb2.StartSignUpResponse(result=build_sign_up_result(result))

    @t.final
    async def rpc_start_sign_in(
        self, request: email_code_pb2.StartSignInRequest, context: "BaseAuthRpcContext"
    ) -> email_code_pb2.StartSignInResponse:
        parameters = AuthStartSignInParameters(
            method=self.METHOD,
            parameters=AuthEmailCodeStart(email=request.email),
            attr_values=build_attr_values(request.attr_values, SESSION_ATTRS),
            transport_attr_values=context.get_transport_attr_values(),
        )
        factory = self.project.auth.sign_in.op_start
        result = await self.rpc_run_operation(factory, parameters, context)
        return email_code_pb2.StartSignInResponse(result=build_sign_in_result(result))
