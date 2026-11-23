"""The metadata over gRPC: its servicer and its binding."""

__all__ = (
    "AuthGrpcMetadataBinding",
    "AuthGrpcMetadataServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.metadata.v1 import metadata_pb2_grpc as metadata_pb2_grpc_temp
from .aliases import AuthGrpcServiceAlias
from .metadata_temp import (
    AuthGrpcMetadataServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcMetadataServicer = AuthGrpcMetadataServicerTemp


class AuthGrpcMetadataBinding:
    auth_metadata_temp = GrpcService(
        metadata_pb2_grpc_temp.MetadataStub, AuthGrpcMetadataServicerTemp
    )
    auth_metadata = AuthGrpcServiceAlias(auth_metadata_temp)
