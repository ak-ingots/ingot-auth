"""The profiles themselves over gRPC: that of the caller, their values."""

__all__ = ("AuthGrpcProfilesServicer",)

import typing as t

from ingot_auth.profiles import (
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsParameters,
)
from ingot_auth.storages import AuthProfileValues

from ..attrs import build_attr_value_message, build_attr_values
from ..base import BaseAuthGrpcServicer, Context
from ingot_auth.profiles.v1 import profiles_pb2, profiles_pb2_grpc


class AuthGrpcProfilesServicer(
    BaseAuthGrpcServicer, profiles_pb2_grpc.ProfilesServicer
):
    """The profile of the caller; the values of the profiles an operator sets."""

    @t.override
    async def GetOwnProfile(
        self, request: profiles_pb2.GetOwnProfileRequest, context: Context
    ) -> profiles_pb2.GetOwnProfileResponse:
        factory = self.project.auth.profiles.op_get_own
        profile = await self.run_operation(factory, None, context)
        return profiles_pb2.GetOwnProfileResponse(
            values=build_values_message(
                AuthProfileValues(
                    tag_ids=profile.tag_ids, attr_values=profile.attr_values
                )
            ),
            permissions=profile.permissions,
            hash=profile.hash,
        )

    @t.override
    async def SetProfileTags(
        self, request: profiles_pb2.SetProfileTagsRequest, context: Context
    ) -> profiles_pb2.SetProfileTagsResponse:
        parameters = AuthSetProfileTagsParameters(
            uid=request.uid, tag_ids=frozenset(request.tag_ids)
        )
        factory = self.project.auth.profiles.op_set_tags
        values = await self.run_operation(factory, parameters, context)
        return profiles_pb2.SetProfileTagsResponse(values=build_values_message(values))

    @t.override
    async def SetProfileAttrValues(
        self, request: profiles_pb2.SetProfileAttrValuesRequest, context: Context
    ) -> profiles_pb2.SetProfileAttrValuesResponse:
        registry = self.project.auth.storage.profiles.attrs.REGISTRY
        parameters = AuthSetProfileAttrValuesParameters(
            uid=request.uid,
            attr_values=build_attr_values(request.attr_values, registry),
        )
        factory = self.project.auth.profiles.op_set_attr_values
        values = await self.run_operation(factory, parameters, context)
        return profiles_pb2.SetProfileAttrValuesResponse(
            values=build_values_message(values)
        )


def build_values_message(values: AuthProfileValues) -> profiles_pb2.ProfileValues:
    """Internal: the message of the values of a profile."""
    return profiles_pb2.ProfileValues(
        tag_ids=sorted(values.tag_ids),
        attr_values=[
            build_attr_value_message(attr_id, value)
            for attr_id, value in sorted(values.attr_values.items())
        ],
    )
