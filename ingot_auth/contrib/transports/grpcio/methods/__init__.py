"""
The methods over gRPC: a servicer a method of the core, each in a binding of
its own, which an application takes with the method; a method of more steps
takes the answers of the flows too, :class:`~..AuthGrpcFlowsBinding`.
"""

__all__ = (
    "AuthGrpcEmailCodeBinding",
    "AuthGrpcEmailCodeServicer",
    "AuthGrpcNicknameBinding",
    "AuthGrpcNicknameServicer",
    "BaseAuthGrpcMethodServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from .base import BaseAuthGrpcMethodServicer
from .email_code import AuthGrpcEmailCodeServicer
from .nickname import AuthGrpcNicknameServicer
from ingot_auth.methods.email_code.v1 import email_code_pb2_grpc
from ingot_auth.methods.nickname.v1 import nickname_pb2_grpc
from ingot_auth.api.methods.email_code.v1 import (
    email_code_pb2_grpc as email_code_pb2_grpc_temp,
)
from ingot_auth.api.methods.nickname.v1 import (
    nickname_pb2_grpc as nickname_pb2_grpc_temp,
)
from .email_code_temp import AuthGrpcEmailCodeServicerTemp
from .nickname_temp import AuthGrpcNicknameServicerTemp


class AuthGrpcNicknameBinding:
    auth_methods_nickname = GrpcService(
        nickname_pb2_grpc.NicknameStub, AuthGrpcNicknameServicer
    )
    auth_methods_nickname_temp = GrpcService(
        nickname_pb2_grpc_temp.NicknameStub, AuthGrpcNicknameServicerTemp
    )


class AuthGrpcEmailCodeBinding:
    auth_methods_email_code = GrpcService(
        email_code_pb2_grpc.EmailCodeStub, AuthGrpcEmailCodeServicer
    )
    auth_methods_email_code_temp = GrpcService(
        email_code_pb2_grpc_temp.EmailCodeStub, AuthGrpcEmailCodeServicerTemp
    )
