"""The metadata over HTTP."""

__all__ = ("AuthStarletteMetadataEndpoint",)

import typing as t

from ingot_starlette.contrib.protobuf import StarletteProtobufRpc
from starlette.requests import Request

from ingot_auth.api import AuthMetadataRpcMixin
from .base import BaseAuthStarletteEndpoint
from ingot_auth.api.metadata.v1 import metadata_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingot_auth.project import AuthProject

SERVICE: t.Final = metadata_pb2.DESCRIPTOR.services_by_name["Metadata"]


class AuthStarletteMetadataEndpoint(AuthMetadataRpcMixin, BaseAuthStarletteEndpoint):
    """
    The metadata, of
    :class:`~ingot_auth.api.AuthMetadataRpcMixin`, open
    to anyone: ``GET /v1/metadata``.
    """

    project: "AuthProject"

    async def get_metadata(
        self, message: metadata_pb2.GetMetadataRequest, request: Request
    ) -> metadata_pb2.GetMetadataResponse:
        return await self.rpc_get_metadata(message, self.get_rpc_context(request))

    @t.override
    def _iter_rpcs(self) -> "Iterator[StarletteProtobufRpc]":
        methods = SERVICE.methods_by_name
        yield StarletteProtobufRpc(
            method=methods["GetMetadata"], handler=self.get_metadata
        )
