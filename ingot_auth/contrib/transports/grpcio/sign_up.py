"""The sign-up over gRPC: its answers."""

__all__ = (
    "AuthGrpcSignUpBinding",
    "AuthGrpcSignUpServicer",
    "build_sign_up_result",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.sign_up.v1 import sign_up_pb2_grpc as sign_up_pb2_grpc_temp
from .aliases import AuthGrpcServiceAlias
from .sign_up_temp import (
    AuthGrpcSignUpServicerTemp,
    build_sign_up_result,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSignUpServicer = AuthGrpcSignUpServicerTemp


class AuthGrpcSignUpBinding:
    auth_sign_up_temp = GrpcService(
        sign_up_pb2_grpc_temp.SignUpStub, AuthGrpcSignUpServicerTemp
    )
    auth_sign_up = AuthGrpcServiceAlias(auth_sign_up_temp)
