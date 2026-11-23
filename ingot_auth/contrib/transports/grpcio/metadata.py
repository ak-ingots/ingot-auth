"""The metadata over gRPC: its servicer and its binding."""

__all__ = ("AuthGrpcMetadataBinding", "AuthGrpcMetadataServicer")

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

from ingot_auth.api import AuthMetadataRpcMixin
from .base import Context, GrpcAuthRpcContext
from ingot_auth.api.metadata.v1 import metadata_pb2, metadata_pb2_grpc

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGrpcMetadataServicer(
    AuthMetadataRpcMixin, GrpcServicer, metadata_pb2_grpc.MetadataServicer
):
    """
    The metadata, of
    :class:`~ingot_auth.api.AuthMetadataRpcMixin`, over gRPC.
    """

    project: "AuthProject"

    @t.override
    async def GetMetadata(
        self, request: metadata_pb2.GetMetadataRequest, context: Context
    ) -> metadata_pb2.GetMetadataResponse:
        return await self.rpc_get_metadata(request, GrpcAuthRpcContext(context))


class AuthGrpcMetadataBinding:
    auth_metadata = GrpcService(
        metadata_pb2_grpc.MetadataStub, AuthGrpcMetadataServicer
    )
