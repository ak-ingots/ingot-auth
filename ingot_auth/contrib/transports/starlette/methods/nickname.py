"""The endpoint of the method of a nickname and a password over HTTP."""

__all__ = ("AuthStarletteNicknameEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthNicknameRpcMixin
from ..base import BaseAuthStarletteEndpoint
from ingot_auth.api.methods.nickname.v1 import nickname_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = nickname_pb2.DESCRIPTOR.services_by_name["Nickname"]


class AuthStarletteNicknameEndpoint(AuthNicknameRpcMixin, BaseAuthStarletteEndpoint):
    """
    The flows of the method of a nickname, of
    :class:`~ingot_auth.api.AuthNicknameRpcMixin`: ``POST
    /v1/methods/nickname:signUp`` and ``:signIn``, of the method in the slot
    ``nickname``.
    """

    METHOD: t.ClassVar[str] = "nickname"

    project: "AuthProject"

    async def sign_up(
        self, message: nickname_pb2.SignUpRequest, request: Request
    ) -> nickname_pb2.SignUpResponse:
        return await self.rpc_sign_up(message, self.get_rpc_context(request))

    async def sign_in(
        self, message: nickname_pb2.SignInRequest, request: Request
    ) -> nickname_pb2.SignInResponse:
        return await self.rpc_sign_in(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(method=methods["SignUp"], handler=self.sign_up)
        yield StarletteProtobufRpc(method=methods["SignIn"], handler=self.sign_in)
