"""The profile of the caller over HTTP."""

__all__ = ("AuthStarletteOwnProfileEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthProfilesRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.api.profiles.v1 import profiles_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = profiles_pb2.DESCRIPTOR.services_by_name["Profiles"]


class AuthStarletteOwnProfileEndpoint(AuthProfilesRpcMixin, BaseAuthStarletteEndpoint):
    """
    The profile of the caller of the token, of
    :class:`~ingot_auth.api.AuthProfilesRpcMixin`, its
    values, its permissions and its hash: ``GET /v1/ownProfile``. Setting the
    values of the profiles, for an operator, is not served over HTTP yet.
    """

    project: "AuthProject"

    async def get_own_profile(
        self, message: profiles_pb2.GetOwnProfileRequest, request: Request
    ) -> profiles_pb2.GetOwnProfileResponse:
        return await self.rpc_get_own_profile(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["GetOwnProfile"], handler=self.get_own_profile
        )
