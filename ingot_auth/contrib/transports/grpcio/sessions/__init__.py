"""The sessions over gRPC: the servicers of their registries and the bindings."""

__all__ = (
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionsBinding",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..proto.ingot_auth.sessions.attrs.v1 import attrs_pb2_grpc
from ..proto.ingot_auth.sessions.presets.v1 import presets_pb2_grpc
from .attrs import AuthGrpcSessionAttrsServicer
from .presets import AuthGrpcSessionPresetsServicer


class AuthGrpcSessionAttrsBinding:
    auth_sessions_attrs = GrpcService(
        attrs_pb2_grpc.AttrsStub, AuthGrpcSessionAttrsServicer
    )


class AuthGrpcSessionPresetsBinding:
    auth_sessions_presets = GrpcService(
        presets_pb2_grpc.PresetsStub, AuthGrpcSessionPresetsServicer
    )


class AuthGrpcSessionsBinding(
    AuthGrpcSessionAttrsBinding, AuthGrpcSessionPresetsBinding
):
    pass
