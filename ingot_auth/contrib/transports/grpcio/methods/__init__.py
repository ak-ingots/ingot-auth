"""
The methods over gRPC: a servicer a method of the core, each in a binding of
its own, which an application takes with the method.
"""

__all__ = ("AuthGrpcNicknameBinding", "AuthGrpcNicknameServicer")

from ingot_grpcio.grpc.services import GrpcService

from .nickname import AuthGrpcNicknameServicer
from ingot_auth.methods.nickname.v1 import nickname_pb2_grpc


class AuthGrpcNicknameBinding:
    auth_methods_nickname = GrpcService(
        nickname_pb2_grpc.NicknameStub, AuthGrpcNicknameServicer
    )
