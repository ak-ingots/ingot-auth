"""The activity log over gRPC."""

__all__ = (
    "ACTIONS",
    "AuthGrpcActivitiesBinding",
    "AuthGrpcActivitiesServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.api.activities.v1 import activities_pb2_grpc as activities_pb2_grpc_temp
from .aliases import AuthGrpcServiceAlias
from .activities_temp import (
    ACTIONS,
    AuthGrpcActivitiesServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcActivitiesServicer = AuthGrpcActivitiesServicerTemp


class AuthGrpcActivitiesBinding:
    auth_activities_temp = GrpcService(
        activities_pb2_grpc_temp.ActivitiesStub, AuthGrpcActivitiesServicerTemp
    )
    auth_activities = AuthGrpcServiceAlias(auth_activities_temp)
