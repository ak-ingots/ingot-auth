"""The sessions over gRPC: the servicers of their registries and the bindings."""

__all__ = (
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionBinding",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..proto.ingot_auth.session.attrs.v1 import attrs_pb2_grpc
from ..proto.ingot_auth.session.presets.v1 import presets_pb2_grpc
from .attrs import AuthGrpcSessionAttrsServicer
from .presets import AuthGrpcSessionPresetsServicer


class AuthGrpcSessionAttrsBinding:
    auth_session_attrs = GrpcService(
        attrs_pb2_grpc.AttrsStub, AuthGrpcSessionAttrsServicer
    )


class AuthGrpcSessionPresetsBinding:
    auth_session_presets = GrpcService(
        presets_pb2_grpc.PresetsStub, AuthGrpcSessionPresetsServicer
    )


class AuthGrpcSessionBinding(
    AuthGrpcSessionAttrsBinding, AuthGrpcSessionPresetsBinding
):
    pass
