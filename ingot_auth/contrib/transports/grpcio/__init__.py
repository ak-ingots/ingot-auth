"""
The auth over gRPC, with the extra ``grpcio``: a service per entity, each in a
binding of its own, so that a server serves the ones it should; a public server
the metadata, an internal one the administration too::

    class AppGrpcServer(AuthGrpcMetadataBinding, DefaultGrpcServer):
        pass


    class AppGrpcErrors(AuthGrpcErrors):
        pass

The administration lets nobody in until a subclass of its servicers tells who
is calling (``_get_caller()``).
"""

__all__ = (
    "AuthGrpcAdminBinding",
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcErrors",
    "AuthGrpcMetadataBinding",
    "AuthGrpcMetadataServicer",
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
    "BaseAuthGrpcServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from .errors import AuthGrpcErrors
from .proto.ingot_auth.v1 import (
    attrs_pb2_grpc,
    metadata_pb2_grpc,
    session_attrs_pb2_grpc,
    tags_pb2_grpc,
)
from .servicers import (
    AuthGrpcAttrsServicer,
    AuthGrpcMetadataServicer,
    AuthGrpcSessionAttrsServicer,
    AuthGrpcTagsServicer,
    BaseAuthGrpcServicer,
)


class AuthGrpcMetadataBinding:
    auth_metadata = GrpcService(
        metadata_pb2_grpc.MetadataStub, AuthGrpcMetadataServicer
    )


class AuthGrpcTagsBinding:
    auth_tags = GrpcService(tags_pb2_grpc.TagsStub, AuthGrpcTagsServicer)


class AuthGrpcAttrsBinding:
    auth_attrs = GrpcService(attrs_pb2_grpc.AttrsStub, AuthGrpcAttrsServicer)


class AuthGrpcSessionAttrsBinding:
    auth_session_attrs = GrpcService(
        session_attrs_pb2_grpc.SessionAttrsStub, AuthGrpcSessionAttrsServicer
    )


class AuthGrpcAdminBinding(
    AuthGrpcTagsBinding, AuthGrpcAttrsBinding, AuthGrpcSessionAttrsBinding
):
    pass
