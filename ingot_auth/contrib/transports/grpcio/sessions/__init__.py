"""
The sessions over gRPC: the servicer of the sessions of the caller's own,
those of their registries, and the bindings.
"""

__all__ = (
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
    "AuthGrpcSessionRegistriesBinding",
    "AuthGrpcSessionsBinding",
    "AuthGrpcSessionsServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.sessions.attrs.v1 import attrs_pb2_grpc
from ingot_auth.api.sessions.presets.v1 import presets_pb2_grpc
from ingot_auth.api.sessions.v1 import sessions_pb2_grpc
from .attrs import AuthGrpcSessionAttrsServicer
from .presets import AuthGrpcSessionPresetsServicer
from .sessions import AuthGrpcSessionsServicer


class AuthGrpcSessionsBinding:
    auth_sessions = GrpcService(
        sessions_pb2_grpc.SessionsStub, AuthGrpcSessionsServicer
    )


class AuthGrpcSessionAttrsBinding:
    auth_sessions_attrs = GrpcService(
        attrs_pb2_grpc.AttrsStub, AuthGrpcSessionAttrsServicer
    )


class AuthGrpcSessionPresetsBinding:
    auth_sessions_presets = GrpcService(
        presets_pb2_grpc.PresetsStub, AuthGrpcSessionPresetsServicer
    )


class AuthGrpcSessionRegistriesBinding(
    AuthGrpcSessionAttrsBinding, AuthGrpcSessionPresetsBinding
):
    pass
