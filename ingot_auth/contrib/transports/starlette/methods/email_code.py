"""The endpoint of the method of an email and a code over HTTP."""

__all__ = ("AuthStarletteEmailCodeEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.contrib.transports.contract import AuthEmailCodeRpcMixin
from ..base import BaseAuthStarletteEndpoint
from ingot_auth.methods.email_code.v1 import email_code_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = email_code_pb2.DESCRIPTOR.services_by_name["EmailCode"]


class AuthStarletteEmailCodeEndpoint(AuthEmailCodeRpcMixin, BaseAuthStarletteEndpoint):
    """
    The starts of the method of an email and a code, of
    :class:`~ingot_auth.contrib.transports.contract.AuthEmailCodeRpcMixin`: ``POST
    /v1/methods/emailCode:startSignUp`` and ``:startSignIn``, each asking for
    the code the client answers by the endpoint of its flow.
    """

    METHOD: t.ClassVar[str] = "email_code"

    project: "AuthProject"

    async def start_sign_up(
        self, message: email_code_pb2.StartSignUpRequest, request: Request
    ) -> email_code_pb2.StartSignUpResponse:
        return await self.rpc_start_sign_up(message, self.get_rpc_context(request))

    async def start_sign_in(
        self, message: email_code_pb2.StartSignInRequest, request: Request
    ) -> email_code_pb2.StartSignInResponse:
        return await self.rpc_start_sign_in(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["StartSignUp"], handler=self.start_sign_up
        )
        yield StarletteProtobufRpc(
            method=methods["StartSignIn"], handler=self.start_sign_in
        )
