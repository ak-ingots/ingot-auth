"""The servicer of the members."""

__all__ = ("AuthGrpcMembersServicer",)

import typing as t

from ingot_auth.storages import AuthMembership

from ..base import BaseAuthGrpcServicer, Context
from ingot_auth.access.members.v1 import members_pb2, members_pb2_grpc


class AuthGrpcMembersServicer(BaseAuthGrpcServicer, members_pb2_grpc.MembersServicer):
    """
    The members of the groups for their administrator: its permissions are
    those of the session of the token of the call, by :meth:`_get_caller`.
    """

    @t.override
    async def AddMember(
        self, request: members_pb2.AddMemberRequest, context: Context
    ) -> members_pb2.AddMemberResponse:
        membership = build_membership(request.membership)
        factory = self.project.auth.access.members.op_add
        await self.run_operation(factory, membership, context)
        return members_pb2.AddMemberResponse()

    @t.override
    async def RemoveMember(
        self, request: members_pb2.RemoveMemberRequest, context: Context
    ) -> members_pb2.RemoveMemberResponse:
        membership = build_membership(request.membership)
        factory = self.project.auth.access.members.op_remove
        await self.run_operation(factory, membership, context)
        return members_pb2.RemoveMemberResponse()

    @t.override
    async def ListMembers(
        self, request: members_pb2.ListMembersRequest, context: Context
    ) -> members_pb2.ListMembersResponse:
        factory = self.project.auth.access.members.op_list
        uids = await self.run_operation(factory, request.group, context)
        return members_pb2.ListMembersResponse(uids=uids)

    @t.override
    async def ListMemberGroups(
        self, request: members_pb2.ListMemberGroupsRequest, context: Context
    ) -> members_pb2.ListMemberGroupsResponse:
        factory = self.project.auth.access.members.op_list_groups
        groups = await self.run_operation(factory, request.uid, context)
        return members_pb2.ListMemberGroupsResponse(groups=groups)


def build_membership(message: members_pb2.Membership) -> AuthMembership:
    """Internal: the membership of a message."""
    return AuthMembership(group=message.group, uid=message.uid)
