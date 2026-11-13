"""The servicer of the method of a nickname and a password."""

__all__ = ("AuthGrpcNicknameServicer",)

import typing as t

from ingot_grpcio.grpc.services import GrpcServicer

from ingot_auth.methods.nickname import AuthNicknameStart
from ingot_auth.sign_in import AuthStartSignInParameters
from ingot_auth.sign_up import AuthStartSignUpParameters

from ..base import Context
from ..sessions.attrs import build_attr_values
from ..sign_in import build_sign_in_result
from ..sign_up import build_sign_up_result
from ingot_auth.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcNicknameServicer(GrpcServicer, nickname_pb2_grpc.NicknameServicer):
    """
    The flows of the method of a nickname, open to anyone, as every flow is:
    they run for the anonymous caller of the project, whatever a call bears,
    given the flags of the flows by the group ``grp_anonymous``. :attr:`METHOD`
    is the name of the slot of the method it serves,
    ``nickname``: an application binding the method under another name
    subclasses it.
    """

    # the name of the method served: the path of its slot in the methods
    METHOD: t.ClassVar[str] = "nickname"

    project: "AuthProject"

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
