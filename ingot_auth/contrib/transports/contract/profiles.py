"""The profiles as messages: the RPCs of their service, of no transport."""

__all__ = ("AuthProfilesRpcMixin", "build_values_message")

import typing as t

from ingot_auth.profiles import (
    AuthSetProfileAttrValuesParameters,
    AuthSetProfileTagsParameters,
)
from ingot_auth.storages import AuthProfileValues

from .attrs import build_attr_value_message, build_attr_values
from .base import AuthSessionRpcMixin
from ingot_auth.profiles.v1 import profiles_pb2

if t.TYPE_CHECKING:
    from .context import BaseAuthRpcContext


class AuthProfilesRpcMixin(AuthSessionRpcMixin):
    """The profile of the caller; the values of the profiles an operator sets."""

    @t.final
    async def rpc_get_own_profile(
        self, request: profiles_pb2.GetOwnProfileRequest, context: "BaseAuthRpcContext"
    ) -> profiles_pb2.GetOwnProfileResponse:
        factory = self.project.auth.profiles.op_get_own
        profile = await self.rpc_run_operation(factory, None, context)
        return profiles_pb2.GetOwnProfileResponse(
            values=build_values_message(
                AuthProfileValues(
                    tag_uids=profile.tag_uids, attr_values=profile.attr_values
                )
            ),
            permissions=profile.permissions,
            hash=profile.hash,
        )

    @t.final
    async def rpc_set_profile_tags(
        self, request: profiles_pb2.SetProfileTagsRequest, context: "BaseAuthRpcContext"
    ) -> profiles_pb2.SetProfileTagsResponse:
        parameters = AuthSetProfileTagsParameters(
            uid=request.uid, tag_uids=frozenset(request.tag_uids)
        )
        factory = self.project.auth.profiles.op_set_tags
        values = await self.rpc_run_operation(factory, parameters, context)
        return profiles_pb2.SetProfileTagsResponse(values=build_values_message(values))

    @t.final
    async def rpc_set_profile_attr_values(
        self,
        request: profiles_pb2.SetProfileAttrValuesRequest,
        context: "BaseAuthRpcContext",
    ) -> profiles_pb2.SetProfileAttrValuesResponse:
        registry = self.project.auth.storage.profiles.attrs.REGISTRY
        parameters = AuthSetProfileAttrValuesParameters(
            uid=request.uid,
            attr_values=build_attr_values(request.attr_values, registry),
        )
        factory = self.project.auth.profiles.op_set_attr_values
        values = await self.rpc_run_operation(factory, parameters, context)
        return profiles_pb2.SetProfileAttrValuesResponse(
            values=build_values_message(values)
        )


def build_values_message(values: AuthProfileValues) -> profiles_pb2.ProfileValues:
    """Internal: the message of the values of a profile."""
    return profiles_pb2.ProfileValues(
        tag_uids=sorted(values.tag_uids),
        attr_values=[
            build_attr_value_message(attr_uid, value)
            for attr_uid, value in sorted(values.attr_values.items())
        ],
    )
