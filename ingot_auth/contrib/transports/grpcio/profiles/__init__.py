"""The profiles over gRPC: the servicers of their registries and the bindings."""

__all__ = (
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcProfilesBinding",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..proto.ingot_auth.profiles.attrs.v1 import attrs_pb2_grpc
from ..proto.ingot_auth.profiles.tags.v1 import tags_pb2_grpc
from .attrs import AuthGrpcAttrsServicer
from .tags import AuthGrpcTagsServicer


class AuthGrpcTagsBinding:
    auth_profiles_tags = GrpcService(tags_pb2_grpc.TagsStub, AuthGrpcTagsServicer)


class AuthGrpcAttrsBinding:
    auth_profiles_attrs = GrpcService(attrs_pb2_grpc.AttrsStub, AuthGrpcAttrsServicer)


class AuthGrpcProfilesBinding(AuthGrpcTagsBinding, AuthGrpcAttrsBinding):
    pass
