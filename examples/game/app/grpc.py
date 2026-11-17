from ingot_grpcio.grpc import GrpcUnit
from ingot_grpcio.grpc.servers import DefaultGrpcServer, GrpcServersUnit
from ingots.puer import Slot

from ingot_auth.contrib.transports.grpcio import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcErrorsUnit,
    AuthGrpcFlowsBinding,
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcProfilesBinding,
)


class AppGrpcServer(
    AuthGrpcMetadataBinding,
    AuthGrpcNicknameBinding,
    AuthGrpcEmailCodeBinding,
    AuthGrpcFlowsBinding,
    AuthGrpcProfilesBinding,
    DefaultGrpcServer,
):
    pass


class AppGrpcServersUnit(GrpcServersUnit):
    default = Slot(AppGrpcServer)


class AppGrpcUnit(GrpcUnit):
    errors = Slot(AuthGrpcErrorsUnit)
    servers = Slot(AppGrpcServersUnit)
