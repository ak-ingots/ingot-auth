"""
The servicer of the method of a nickname and a password, of
:mod:`ingot_auth.api`. Temporary: its names suffixed ``Temp``, its services
bound as ``*_temp`` beside the old ones, till the old API is removed.
"""

__all__ = ("AuthGrpcNicknameServicerTemp",)

import typing as t

from ingot_auth.api import AuthNicknameRpcMixin
from ..base import Context
from .base import BaseAuthGrpcMethodServicer
from ingot_auth.api.methods.nickname.v1 import nickname_pb2, nickname_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcNicknameServicerTemp(
    AuthNicknameRpcMixin, BaseAuthGrpcMethodServicer, nickname_pb2_grpc.NicknameServicer
):
    """
    The flows of the method of a nickname, of
    :class:`~ingot_auth.api.AuthNicknameRpcMixin`, over gRPC.
    """

    METHOD: t.ClassVar[str] = "nickname"

    project: "AuthProject"

    @t.override
    async def SignUp(
        self, request: nickname_pb2.SignUpRequest, context: Context
    ) -> nickname_pb2.SignUpResponse:
        return await self.rpc_sign_up(request, self.get_rpc_context(context))

    @t.override
    async def SignIn(
        self, request: nickname_pb2.SignInRequest, context: Context
    ) -> nickname_pb2.SignInResponse:
        return await self.rpc_sign_in(request, self.get_rpc_context(context))
