"""
The command line of the game: those of the auth and of gRPC joined, ``auth
...`` the operator's, ``grpc export`` the SDKs of the clients.
"""

from ingot_grpcio.grpc import GrpcCliUnit

from ingot_auth.cli import AuthCliUnit


class AppCliUnit(AuthCliUnit, GrpcCliUnit):
    pass
