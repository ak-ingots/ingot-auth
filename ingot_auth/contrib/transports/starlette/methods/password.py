"""The endpoint of the password of the profile of the caller over HTTP."""

__all__ = ("AuthStarlettePasswordEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthPasswordRpcMixin
from ..base import BaseAuthStarletteEndpoint
from ingot_auth.api.methods.password.v1 import password_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = password_pb2.DESCRIPTOR.services_by_name["Password"]


class AuthStarlettePasswordEndpoint(AuthPasswordRpcMixin, BaseAuthStarletteEndpoint):
    """
    The change of the password of the caller of the token, of
    :class:`~ingot_auth.api.AuthPasswordRpcMixin`, ``Authorization: Bearer
    <token>``: ``POST /v1/methods/password:change``.
    """

    project: "AuthProject"

    async def change_password(
        self, message: password_pb2.ChangePasswordRequest, request: Request
    ) -> password_pb2.ChangePasswordResponse:
        return await self.rpc_change_password(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["ChangePassword"], handler=self.change_password
        )
