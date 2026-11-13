"""The servicer of the method of a nickname and a password."""

__all__ = ("AuthGrpcNicknameServicer",)

import typing as t

from ingot_auth.methods.nickname import AuthNicknameStart
from ingot_auth.sign_in import AuthStartSignInParameters
from ingot_auth.sign_up import AuthStartSignUpParameters

from ..base import Context
from ..sessions.attrs import build_attr_values
from ..sign_in import build_sign_in_result
from ..sign_up import build_sign_up_result
from .base import BaseAuthGrpcMethodServicer
from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc


class AuthGrpcNicknameServicer(
    BaseAuthGrpcMethodServicer, nickname_pb2_grpc.NicknameServicer
):
    """
    The flows of the method of a nickname, each of one step, of the method
    in the slot ``nickname``.
    """

    METHOD: t.ClassVar[str] = "nickname"

    @t.override
    async def SignUp(
        self, request: nickname_pb2.SignUpRequest, context: Context
    ) -> nickname_pb2.SignUpResponse:
        parameters = AuthStartSignUpParameters(
            method=self.METHOD,
            parameters=AuthNicknameStart(
                nickname=request.nickname, password=request.password
            ),
            attr_values=build_attr_values(request.attr_values),
            transport_attr_values=self.get_transport_attr_values(context),
        )
        factory = self.project.auth.sign_up.op_start
        result = await self.run_operation(factory, parameters, context)
        return nickname_pb2.SignUpResponse(result=build_sign_up_result(result))

    @t.override
    async def SignIn(
        self, request: nickname_pb2.SignInRequest, context: Context
    ) -> nickname_pb2.SignInResponse:
        parameters = AuthStartSignInParameters(
            method=self.METHOD,
            parameters=AuthNicknameStart(
                nickname=request.nickname, password=request.password
            ),
            attr_values=build_attr_values(request.attr_values),
            transport_attr_values=self.get_transport_attr_values(context),
        )
        factory = self.project.auth.sign_in.op_start
        result = await self.run_operation(factory, parameters, context)
        return nickname_pb2.SignInResponse(result=build_sign_in_result(result))
