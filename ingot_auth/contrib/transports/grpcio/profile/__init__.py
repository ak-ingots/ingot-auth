"""The profiles over gRPC: the servicers of their registries and the bindings."""

__all__ = (
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcProfileBinding",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..proto.ingot_auth.profile.attrs.v1 import attrs_pb2_grpc
from ..proto.ingot_auth.profile.tags.v1 import tags_pb2_grpc
from .attrs import AuthGrpcAttrsServicer
from .tags import AuthGrpcTagsServicer


class AuthGrpcTagsBinding:
    auth_profile_tags = GrpcService(tags_pb2_grpc.TagsStub, AuthGrpcTagsServicer)


class AuthGrpcAttrsBinding:
    auth_profile_attrs = GrpcService(attrs_pb2_grpc.AttrsStub, AuthGrpcAttrsServicer)


class AuthGrpcProfileBinding(AuthGrpcTagsBinding, AuthGrpcAttrsBinding):
    pass
