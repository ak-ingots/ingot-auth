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

from ingot_auth.profiles.attrs.v1 import attrs_pb2_grpc
from ingot_auth.profiles.tags.v1 import tags_pb2_grpc
from ingot_auth.profiles.v1 import profiles_pb2_grpc
from .attrs import AuthGrpcAttrsServicer
from .profiles import AuthGrpcProfilesServicer
from .tags import AuthGrpcTagsServicer
from ingot_auth.api.profiles.attrs.v1 import attrs_pb2_grpc as attrs_pb2_grpc_temp
from ingot_auth.api.profiles.tags.v1 import tags_pb2_grpc as tags_pb2_grpc_temp
from ingot_auth.api.profiles.v1 import profiles_pb2_grpc as profiles_pb2_grpc_temp
from .attrs_temp import AuthGrpcAttrsServicerTemp
from .profiles_temp import AuthGrpcProfilesServicerTemp
from .tags_temp import AuthGrpcTagsServicerTemp


class AuthGrpcProfilesBinding:
    auth_profiles = GrpcService(
        profiles_pb2_grpc.ProfilesStub, AuthGrpcProfilesServicer
    )
    auth_profiles_temp = GrpcService(
        profiles_pb2_grpc_temp.ProfilesStub, AuthGrpcProfilesServicerTemp
    )


class AuthGrpcTagsBinding:
    auth_profiles_tags = GrpcService(tags_pb2_grpc.TagsStub, AuthGrpcTagsServicer)
    auth_profiles_tags_temp = GrpcService(
        tags_pb2_grpc_temp.TagsStub, AuthGrpcTagsServicerTemp
    )


class AuthGrpcAttrsBinding:
    auth_profiles_attrs = GrpcService(attrs_pb2_grpc.AttrsStub, AuthGrpcAttrsServicer)
    auth_profiles_attrs_temp = GrpcService(
        attrs_pb2_grpc_temp.AttrsStub, AuthGrpcAttrsServicerTemp
    )


class AuthGrpcProfileRegistriesBinding(AuthGrpcTagsBinding, AuthGrpcAttrsBinding):
    pass
