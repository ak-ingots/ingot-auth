"""The answers of the sign-in over HTTP."""

__all__ = ("AuthStarletteSignInEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthSignInRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.api.sign_in.v1 import sign_in_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = sign_in_pb2.DESCRIPTOR.services_by_name["SignIn"]


class AuthStarletteSignInEndpoint(AuthSignInRpcMixin, BaseAuthStarletteEndpoint):
    """
    The answers of a sign-in, of
    :class:`~ingot_auth.api.AuthSignInRpcMixin`, by any
    method or factor of more steps: ``POST /v1/signIn:answer``.
    """

    project: "AuthProject"

    async def answer_sign_in(
        self, message: sign_in_pb2.AnswerSignInRequest, request: Request
    ) -> sign_in_pb2.AnswerSignInResponse:
        return await self.rpc_answer_sign_in(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["AnswerSignIn"], handler=self.answer_sign_in
        )
