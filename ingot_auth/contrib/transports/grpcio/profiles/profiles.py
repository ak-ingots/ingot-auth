"""The profiles themselves over gRPC: that of the caller, their values."""

__all__ = ("AuthGrpcProfilesServicer",)

import typing as t

from ingot_auth.contrib.transports.contract import AuthProfilesRpcMixin
from ..base import BaseAuthGrpcServicer, Context, GrpcAuthRpcContext
from ingot_auth.profiles.v1 import profiles_pb2, profiles_pb2_grpc


class AuthGrpcProfilesServicer(
    AuthProfilesRpcMixin, BaseAuthGrpcServicer, profiles_pb2_grpc.ProfilesServicer
):
    """
    The profiles, of
    :class:`~ingot_auth.contrib.transports.contract.AuthProfilesRpcMixin`, over gRPC.
    """

    @t.override
    async def GetOwnProfile(
        self, request: profiles_pb2.GetOwnProfileRequest, context: Context
    ) -> profiles_pb2.GetOwnProfileResponse:
        return await self.rpc_get_own_profile(request, GrpcAuthRpcContext(context))

    @t.override
    async def SetProfileTags(
        self, request: profiles_pb2.SetProfileTagsRequest, context: Context
    ) -> profiles_pb2.SetProfileTagsResponse:
        return await self.rpc_set_profile_tags(request, GrpcAuthRpcContext(context))

    @t.override
    async def SetProfileAttrValues(
        self, request: profiles_pb2.SetProfileAttrValuesRequest, context: Context
    ) -> profiles_pb2.SetProfileAttrValuesResponse:
        return await self.rpc_set_profile_attr_values(
            request, GrpcAuthRpcContext(context)
        )
