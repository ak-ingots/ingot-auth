"""The sign-out over HTTP."""

__all__ = ("AuthStarletteSignOutEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ..contract import AuthSignOutRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.sign_out.v1 import sign_out_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = sign_out_pb2.DESCRIPTOR.services_by_name["SignOut"]


class AuthStarletteSignOutEndpoint(AuthSignOutRpcMixin, BaseAuthStarletteEndpoint):
    """
    The sign-out, of
    :class:`~ingot_auth.contrib.transports.contract.AuthSignOutRpcMixin`, of the
    caller of the token, ``Authorization: Bearer <token>``: ``POST
    /v1/session:signOut``.
    """

    project: "AuthProject"

    async def sign_out(
        self, message: sign_out_pb2.SignOutRequest, request: Request
    ) -> sign_out_pb2.SignOutResponse:
        return await self.rpc_sign_out(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(method=methods["SignOut"], handler=self.sign_out)
