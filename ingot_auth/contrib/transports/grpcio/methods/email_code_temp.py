"""
The servicer of the method of an email and a code sent to it, of
:mod:`ingot_auth.api`. Temporary: its names suffixed ``Temp``, its services
bound as ``*_temp`` beside the old ones, till the old API is removed.
"""

__all__ = ("AuthGrpcEmailCodeServicerTemp",)

import typing as t

from ingot_auth.api import AuthEmailCodeRpcMixin
from ..base import Context
from .base import BaseAuthGrpcMethodServicer
from ingot_auth.api.methods.email_code.v1 import email_code_pb2, email_code_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcEmailCodeServicerTemp(
    AuthEmailCodeRpcMixin,
    BaseAuthGrpcMethodServicer,
    email_code_pb2_grpc.EmailCodeServicer,
):
    """
    The starts of the method of an email and a code, of
    :class:`~ingot_auth.api.AuthEmailCodeRpcMixin`, over gRPC.
    """

    METHOD: t.ClassVar[str] = "email_code"

    project: "AuthProject"

    @t.override
    async def StartSignUp(
        self, request: email_code_pb2.StartSignUpRequest, context: Context
    ) -> email_code_pb2.StartSignUpResponse:
        return await self.rpc_start_sign_up(request, self.get_rpc_context(context))

    @t.override
    async def StartSignIn(
        self, request: email_code_pb2.StartSignInRequest, context: Context
    ) -> email_code_pb2.StartSignInResponse:
        return await self.rpc_start_sign_in(request, self.get_rpc_context(context))
