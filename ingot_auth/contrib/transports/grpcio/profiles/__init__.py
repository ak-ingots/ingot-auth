"""
The profiles over gRPC: the servicer of their values, those of their
registries, and the bindings.
"""

__all__ = (
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcProfileRegistriesBinding",
    "AuthGrpcProfilesBinding",
    "AuthGrpcProfilesServicer",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.profiles.attrs.v1 import attrs_pb2_grpc
from ingot_auth.api.profiles.tags.v1 import tags_pb2_grpc
from ingot_auth.api.profiles.v1 import profiles_pb2_grpc
from .attrs import AuthGrpcAttrsServicer
from .profiles import AuthGrpcProfilesServicer
from .tags import AuthGrpcTagsServicer


class AuthGrpcProfilesBinding:
    auth_profiles = GrpcService(
        profiles_pb2_grpc.ProfilesStub, AuthGrpcProfilesServicer
    )


class AuthGrpcTagsBinding:
    auth_profiles_tags = GrpcService(tags_pb2_grpc.TagsStub, AuthGrpcTagsServicer)


class AuthGrpcAttrsBinding:
    auth_profiles_attrs = GrpcService(attrs_pb2_grpc.AttrsStub, AuthGrpcAttrsServicer)


class AuthGrpcProfileRegistriesBinding(AuthGrpcTagsBinding, AuthGrpcAttrsBinding):
    pass
