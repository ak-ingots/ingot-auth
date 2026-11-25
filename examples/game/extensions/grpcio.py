"""
gRPC in the game: the server of the players, the services of the auth
bound to it, the errors encoded by the auth's policies.
"""

from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.servers import DefaultGrpcServer, GrpcServersUnit
from ingots.puer import Slot

from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcErrorsUnit,
    AuthGrpcFlowsBinding,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcPasswordBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
)


class AppGrpcServer(
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcPasswordBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionsBinding,
    DefaultGrpcServer,
):
    pass


class AppGrpcServersUnit(GrpcServersUnit):
    default = Slot(AppGrpcServer)


class AppGrpcUnit(GrpcUnit):
    errors = Slot(AuthGrpcErrorsUnit)
    servers = Slot(AppGrpcServersUnit)
