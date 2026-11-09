"""The access over gRPC: the servicers of the groups and the members, bound."""

__all__ = (
    "AuthGrpcAccessBinding",
    "AuthGrpcGroupsBinding",
    "AuthGrpcGroupsServicer",
    "AuthGrpcMembersBinding",
    "AuthGrpcMembersServicer",
)

from ingot_grpcio.grpc.services import GrpcService

from ..proto.ingot_auth.access.groups.v1 import groups_pb2_grpc
from ..proto.ingot_auth.access.members.v1 import members_pb2_grpc
from .groups import AuthGrpcGroupsServicer
from .members import AuthGrpcMembersServicer


class AuthGrpcGroupsBinding:
    auth_access_groups = GrpcService(groups_pb2_grpc.GroupsStub, AuthGrpcGroupsServicer)


class AuthGrpcMembersBinding:
    auth_access_members = GrpcService(
        members_pb2_grpc.MembersStub, AuthGrpcMembersServicer
    )


class AuthGrpcAccessBinding(AuthGrpcGroupsBinding, AuthGrpcMembersBinding):
    pass
