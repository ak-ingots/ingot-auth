"""The access over gRPC: the servicers of the groups and the members, bound."""

__all__ = (
    "AuthGrpcAccessBinding",
    "AuthGrpcGroupsBinding",
    "AuthGrpcGroupsServicer",
    "AuthGrpcMembersBinding",
    "AuthGrpcMembersServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..aliases import AuthGrpcServiceAlias

from .groups import AuthGrpcGroupsServicer
from .members import AuthGrpcMembersServicer
from ingot_auth.api.access.groups.v1 import groups_pb2_grpc as groups_pb2_grpc_temp
from ingot_auth.api.access.members.v1 import members_pb2_grpc as members_pb2_grpc_temp
from .groups_temp import AuthGrpcGroupsServicerTemp
from .members_temp import AuthGrpcMembersServicerTemp


class AuthGrpcGroupsBinding:
    auth_access_groups_temp = GrpcService(
        groups_pb2_grpc_temp.GroupsStub, AuthGrpcGroupsServicerTemp
    )
    auth_access_groups = AuthGrpcServiceAlias(auth_access_groups_temp)


class AuthGrpcMembersBinding:
    auth_access_members_temp = GrpcService(
        members_pb2_grpc_temp.MembersStub, AuthGrpcMembersServicerTemp
    )
    auth_access_members = AuthGrpcServiceAlias(auth_access_members_temp)


class AuthGrpcAccessBinding(AuthGrpcGroupsBinding, AuthGrpcMembersBinding):
    pass
