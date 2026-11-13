"""The servicer of the method of an email and a code sent to it."""

__all__ = ("AuthGrpcEmailCodeServicer",)

import typing as t

from ingot_auth.methods.email_code import AuthEmailCodeStart
from ingot_auth.sign_in import AuthStartSignInParameters
from ingot_auth.sign_up import AuthStartSignUpParameters

from ..base import Context
from ..sessions.attrs import build_attr_values
from ..sign_in import build_sign_in_result
from ..sign_up import build_sign_up_result
from .base import BaseAuthGrpcMethodServicer
from ingot_auth.methods.email_code.v1 import email_code_pb2, email_code_pb2_grpc


class AuthGrpcEmailCodeServicer(
    BaseAuthGrpcMethodServicer, email_code_pb2_grpc.EmailCodeServicer
):
    """
    The starts of the method of an email and a code, of the method in the
    slot ``email_code``: each asks for the code, which the client gives by
    the answer of the flow.
    """

    METHOD: t.ClassVar[str] = "email_code"

    @t.override
    async def StartSignUp(
        self, request: email_code_pb2.StartSignUpRequest, context: Context
    ) -> email_code_pb2.StartSignUpResponse:
        parameters = AuthStartSignUpParameters(
            method=self.METHOD,
            parameters=AuthEmailCodeStart(email=request.email),
            attr_values=build_attr_values(request.attr_values),
            transport_attr_values=self.get_transport_attr_values(context),
        )
        factory = self.project.auth.sign_up.op_start
        result = await self.run_operation(factory, parameters, context)
        return email_code_pb2.StartSignUpResponse(result=build_sign_up_result(result))

    @t.override
    async def StartSignIn(
        self, request: email_code_pb2.StartSignInRequest, context: Context
    ) -> email_code_pb2.StartSignInResponse:
        parameters = AuthStartSignInParameters(
            method=self.METHOD,
            parameters=AuthEmailCodeStart(email=request.email),
            attr_values=build_attr_values(request.attr_values),
            transport_attr_values=self.get_transport_attr_values(context),
        )
        factory = self.project.auth.sign_in.op_start
        result = await self.run_operation(factory, parameters, context)
        return email_code_pb2.StartSignInResponse(result=build_sign_in_result(result))
