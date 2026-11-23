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

from ingot_auth.sessions.attrs.v1 import attrs_pb2_grpc
from ingot_auth.sessions.presets.v1 import presets_pb2_grpc
from ingot_auth.sessions.v1 import sessions_pb2_grpc
from .attrs import AuthGrpcSessionAttrsServicer
from .presets import AuthGrpcSessionPresetsServicer
from .sessions import AuthGrpcSessionsServicer
from ingot_auth.api.sessions.attrs.v1 import attrs_pb2_grpc as attrs_pb2_grpc_temp
from ingot_auth.api.sessions.presets.v1 import presets_pb2_grpc as presets_pb2_grpc_temp
from ingot_auth.api.sessions.v1 import sessions_pb2_grpc as sessions_pb2_grpc_temp
from .attrs_temp import AuthGrpcSessionAttrsServicerTemp
from .presets_temp import AuthGrpcSessionPresetsServicerTemp
from .sessions_temp import AuthGrpcSessionsServicerTemp


class AuthGrpcSessionsBinding:
    auth_sessions = GrpcService(
        sessions_pb2_grpc.SessionsStub, AuthGrpcSessionsServicer
    )
    auth_sessions_temp = GrpcService(
        sessions_pb2_grpc_temp.SessionsStub, AuthGrpcSessionsServicerTemp
    )


class AuthGrpcSessionAttrsBinding:
    auth_sessions_attrs = GrpcService(
        attrs_pb2_grpc.AttrsStub, AuthGrpcSessionAttrsServicer
    )
    auth_sessions_attrs_temp = GrpcService(
        attrs_pb2_grpc_temp.AttrsStub, AuthGrpcSessionAttrsServicerTemp
    )


class AuthGrpcSessionPresetsBinding:
    auth_sessions_presets = GrpcService(
        presets_pb2_grpc.PresetsStub, AuthGrpcSessionPresetsServicer
    )
    auth_sessions_presets_temp = GrpcService(
        presets_pb2_grpc_temp.PresetsStub, AuthGrpcSessionPresetsServicerTemp
    )


class AuthGrpcSessionRegistriesBinding(
    AuthGrpcSessionAttrsBinding, AuthGrpcSessionPresetsBinding
):
    pass
