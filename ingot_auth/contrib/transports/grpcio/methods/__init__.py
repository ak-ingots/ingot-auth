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
)

from ingot_grpcio.grpc.services import GrpcService

from .email_code import AuthGrpcEmailCodeServicer
from .nickname import AuthGrpcNicknameServicer
from ingot_auth.methods.email_code.v1 import email_code_pb2_grpc
from ingot_auth.methods.nickname.v1 import nickname_pb2_grpc


class AuthGrpcNicknameBinding:
    auth_methods_nickname = GrpcService(
        nickname_pb2_grpc.NicknameStub, AuthGrpcNicknameServicer
    )


class AuthGrpcEmailCodeBinding:
    auth_methods_email_code = GrpcService(
        email_code_pb2_grpc.EmailCodeStub, AuthGrpcEmailCodeServicer
    )
