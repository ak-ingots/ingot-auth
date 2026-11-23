"""
The servicer of the groups, of :mod:`ingot_auth.api`. Temporary: its names
suffixed ``Temp``, its services bound as ``*_temp`` beside the old ones,
till the old API is removed.
"""

__all__ = ("AuthGrpcGroupsServicerTemp",)

import typing as t

from ingot_auth.access.groups import AuthGroupInfo

from ..base import BaseAuthGrpcServicer, Context
from ingot_auth.api.access.groups.v1 import groups_pb2, groups_pb2_grpc


class AuthGrpcGroupsServicerTemp(BaseAuthGrpcServicer, groups_pb2_grpc.GroupsServicer):
    """
    The groups for their administrator: its permissions are those of the
    session of the token of the call, by :meth:`_get_caller`.
    """

    @t.override
    async def ListGroups(
        self, request: groups_pb2.ListGroupsRequest, context: Context
    ) -> groups_pb2.ListGroupsResponse:
        groups = await self.run_operation(
            self.project.auth.access.groups.op_list, None, context
        )
        return groups_pb2.ListGroupsResponse(groups=map(build_group_message, groups))


def build_group_message(group: AuthGroupInfo) -> groups_pb2.Group:
    """Internal: the message of a group."""
    return groups_pb2.Group(name=group.name, permissions=dict(group.permissions))
