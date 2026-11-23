"""The sessions of the caller's own over HTTP."""

__all__ = ("AuthStarletteOwnSessionsEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthSessionsRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.api.sessions.v1 import sessions_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = sessions_pb2.DESCRIPTOR.services_by_name["Sessions"]


class AuthStarletteOwnSessionsEndpoint(AuthSessionsRpcMixin, BaseAuthStarletteEndpoint):
    """
    The sessions of the caller of the token, of
    :class:`~ingot_auth.api.AuthSessionsRpcMixin`, its
    own alone: ``GET /v1/ownSessions``, ``POST
    /v1/ownSessions/{session_uid}:revoke``, ``POST
    /v1/ownSessions:revokeOthers``. Those of a profile, for an operator, are not
    served over HTTP yet.
    """

    project: "AuthProject"

    async def list_own_sessions(
        self, message: sessions_pb2.ListOwnSessionsRequest, request: Request
    ) -> sessions_pb2.ListOwnSessionsResponse:
        return await self.rpc_list_own_sessions(message, self.get_rpc_context(request))

    async def revoke_own_session(
        self, message: sessions_pb2.RevokeOwnSessionRequest, request: Request
    ) -> sessions_pb2.RevokeOwnSessionResponse:
        return await self.rpc_revoke_own_session(message, self.get_rpc_context(request))

    async def revoke_other_sessions(
        self, message: sessions_pb2.RevokeOtherSessionsRequest, request: Request
    ) -> sessions_pb2.RevokeOtherSessionsResponse:
        return await self.rpc_revoke_other_sessions(
            message, self.get_rpc_context(request)
        )

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["ListOwnSessions"], handler=self.list_own_sessions
        )
        yield StarletteProtobufRpc(
            method=methods["RevokeOwnSession"], handler=self.revoke_own_session
        )
        yield StarletteProtobufRpc(
            method=methods["RevokeOtherSessions"], handler=self.revoke_other_sessions
        )
