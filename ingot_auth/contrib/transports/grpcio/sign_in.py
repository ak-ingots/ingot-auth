"""The sign-in over gRPC: its answers."""

__all__ = (
    "AuthGrpcSignInBinding",
    "AuthGrpcSignInServicer",
    "build_sign_in_result",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.sign_in.v1 import sign_in_pb2_grpc as sign_in_pb2_grpc_temp
from .aliases import AuthGrpcServiceAlias
from .sign_in_temp import (
    AuthGrpcSignInServicerTemp,
    build_sign_in_result,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSignInServicer = AuthGrpcSignInServicerTemp


class AuthGrpcSignInBinding:
    auth_sign_in_temp = GrpcService(
        sign_in_pb2_grpc_temp.SignInStub, AuthGrpcSignInServicerTemp
    )
    auth_sign_in = AuthGrpcServiceAlias(auth_sign_in_temp)
