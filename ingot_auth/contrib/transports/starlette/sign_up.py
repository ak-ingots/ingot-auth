"""The answers of the sign-up over HTTP."""

__all__ = ("AuthStarletteSignUpEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ..contract import AuthSignUpRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.sign_up.v1 import sign_up_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = sign_up_pb2.DESCRIPTOR.services_by_name["SignUp"]


class AuthStarletteSignUpEndpoint(AuthSignUpRpcMixin, BaseAuthStarletteEndpoint):
    """
    The answers of a sign-up, of
    :class:`~ingot_auth.contrib.transports.contract.AuthSignUpRpcMixin`, by any
    method of more steps: ``POST /v1/signUp:answer``.
    """

    project: "AuthProject"

    async def answer_sign_up(
        self, message: sign_up_pb2.AnswerSignUpRequest, request: Request
    ) -> sign_up_pb2.AnswerSignUpResponse:
        return await self.rpc_answer_sign_up(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["AnswerSignUp"], handler=self.answer_sign_up
        )
