"""The RPCs of the method of a nickname and a password."""

__all__ = ("AuthNicknameRpcMixin",)

import typing as t

from ingot_auth.methods.nickname import AuthNicknameStart
from ingot_auth.sign_in import AuthStartSignInParameters
from ingot_auth.sign_up import AuthStartSignUpParameters

from ingot_auth.api.attrs.values import SESSION_ATTRS, build_attr_values
from ingot_auth.api.results import build_sign_in_result, build_sign_up_result
from ..base import BaseAuthMethodRpcMixin
from .v1 import nickname_pb2

if t.TYPE_CHECKING:
    from ingot_auth.api.context import BaseAuthRpcContext


class AuthNicknameRpcMixin(BaseAuthMethodRpcMixin):
    """
    The flows of the method of a nickname, each of one step, of the method
    in the slot ``nickname``.
    """

    METHOD: t.ClassVar[str] = "nickname"

    @t.final
    async def rpc_sign_up(
        self, request: nickname_pb2.SignUpRequest, context: "BaseAuthRpcContext"
    ) -> nickname_pb2.SignUpResponse:
        parameters = AuthStartSignUpParameters(
            method=self.METHOD,
            parameters=AuthNicknameStart(
                nickname=request.nickname, password=request.password
            ),
            attr_values=build_attr_values(request.attr_values, SESSION_ATTRS),
            transport_attr_values=context.get_transport_attr_values(),
        )
        factory = self.project.auth.sign_up.op_start
        result = await self.rpc_run_operation(factory, parameters, context)
        return nickname_pb2.SignUpResponse(result=build_sign_up_result(result))

    @t.final
    async def rpc_sign_in(
        self, request: nickname_pb2.SignInRequest, context: "BaseAuthRpcContext"
    ) -> nickname_pb2.SignInResponse:
        parameters = AuthStartSignInParameters(
            method=self.METHOD,
            parameters=AuthNicknameStart(
                nickname=request.nickname, password=request.password
            ),
            attr_values=build_attr_values(request.attr_values, SESSION_ATTRS),
            transport_attr_values=context.get_transport_attr_values(),
        )
        factory = self.project.auth.sign_in.op_start
        result = await self.rpc_run_operation(factory, parameters, context)
        return nickname_pb2.SignInResponse(result=build_sign_in_result(result))
