"""The servicer of the method of a nickname and a password."""

__all__ = ("AuthGrpcNicknameServicer",)

import dataclasses
import typing as t

from ingots.defaults.operations import ANONYMOUS_CALLER, Caller, Permissions

from ingot_auth.methods.nickname import AuthNicknameStart
from ingot_auth.sign_in import AuthSignInPermissions, AuthStartSignInParameters
from ingot_auth.sign_up import AuthSignUpPermissions, AuthStartSignUpParameters

from ..base import BaseAuthGrpcServicer, Context
from ..sessions.attrs import build_attr_values
from ..sign_in import build_sign_in_result
from ..sign_up import build_sign_up_result
from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc


class AuthGrpcNicknameServicer(
    BaseAuthGrpcServicer, nickname_pb2_grpc.NicknameServicer
):
    """
    The flows of the method of a nickname, open to anyone: they run for the
    anonymous caller of :meth:`_get_anonymous_caller`, given the flags of the
    sign-up and of the sign-in, and those of the methods whose flows their
    toggles open. :attr:`METHOD` is the name of the slot of the method it
    serves, ``nickname``: an application binding the method under another
    name subclasses it.
    """

    # the name of the method served: the path of its slot in the methods
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
        )
        factory = self.project.auth.sign_in.op_start
        result = await self.run_operation(factory, parameters, context)
        return nickname_pb2.SignInResponse(result=build_sign_in_result(result))

    @t.override
    def _get_anonymous_caller(self) -> Caller:
        flows = Permissions(
            AuthSignUpPermissions.CAN_SIGN_UP, AuthSignInPermissions.CAN_SIGN_IN
        )
        methods = self.project.auth.methods.get_anonymous_permissions()
        return dataclasses.replace(ANONYMOUS_CALLER, permissions=flows | methods)
