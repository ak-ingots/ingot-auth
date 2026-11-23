"""The sign-out over gRPC."""

__all__ = (
    "AuthGrpcSignOutBinding",
    "AuthGrpcSignOutServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.sign_out.v1 import sign_out_pb2_grpc as sign_out_pb2_grpc_temp
from .aliases import AuthGrpcServiceAlias
from .sign_out_temp import (
    AuthGrpcSignOutServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSignOutServicer = AuthGrpcSignOutServicerTemp


class AuthGrpcSignOutBinding:
    auth_sign_out_temp = GrpcService(
        sign_out_pb2_grpc_temp.SignOutStub, AuthGrpcSignOutServicerTemp
    )
    auth_sign_out = AuthGrpcServiceAlias(auth_sign_out_temp)
