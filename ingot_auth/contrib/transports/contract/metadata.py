"""The metadata as messages: the RPC of its service, of no transport."""

__all__ = (
    "AuthMetadataRpcMixin",
    "build_method_message",
    "build_profile_message",
    "build_session_message",
)

import typing as t

from ingot_auth.metadata import (
    AuthMethodMetadata,
    AuthProfileMetadata,
    AuthSessionMetadata,
)
from ingot_auth.storages import AuthAttrType

from .base import AuthRpcMixin
from ingot_auth.metadata.v1 import metadata_pb2

if t.TYPE_CHECKING:
    from .context import BaseAuthRpcContext

ATTR_TYPES: t.Final = {
    AuthAttrType.BOOL: metadata_pb2.ATTR_TYPE_BOOL,
    AuthAttrType.INT: metadata_pb2.ATTR_TYPE_INT,
    AuthAttrType.DECIMAL: metadata_pb2.ATTR_TYPE_DECIMAL,
    AuthAttrType.DATETIME: metadata_pb2.ATTR_TYPE_DATETIME,
    AuthAttrType.STR: metadata_pb2.ATTR_TYPE_STR,
}


class AuthMetadataRpcMixin(AuthRpcMixin):
    """
    The metadata, public unless told otherwise: a client asks for it before
    signing in, so it runs for the anonymous caller of the project, whatever
    a call bears, whom the group ``auth.grp_anonymous`` grants ``CAN_READ``; an
    application closes it by taking the flag off in that group, its class in
    its slot.
    """

    @t.final
    async def rpc_get_metadata(
        self, request: metadata_pb2.GetMetadataRequest, context: "BaseAuthRpcContext"
    ) -> metadata_pb2.GetMetadataResponse:
        metadata = await self.rpc_run_operation(
            self.project.auth.metadata.op_get, None, context
        )
        return metadata_pb2.GetMetadataResponse(
            profile=build_profile_message(metadata.profile),
            session=build_session_message(metadata.session),
            methods=(build_method_message(method) for method in metadata.methods),
        )


def build_profile_message(profile: AuthProfileMetadata) -> metadata_pb2.Profile:
    """Internal: the message of the metadata of the profiles."""
    return metadata_pb2.Profile(
        tags=(
            metadata_pb2.Profile.Tag(uid=tag.uid, name=tag.name) for tag in profile.tags
        ),
        attrs=(
            metadata_pb2.Profile.Attr(
                uid=attr.uid, name=attr.name, type=ATTR_TYPES[attr.type]
            )
            for attr in profile.attrs
        ),
    )


def build_session_message(session: AuthSessionMetadata) -> metadata_pb2.Session:
    """Internal: the message of the metadata of the sessions."""
    return metadata_pb2.Session(
        attrs=(
            metadata_pb2.Session.Attr(
                uid=attr.uid, name=attr.name, type=ATTR_TYPES[attr.type]
            )
            for attr in session.attrs
        ),
        presets=(
            metadata_pb2.Session.Preset(uid=preset.uid, name=preset.name)
            for preset in session.presets
        ),
        bindings=(
            metadata_pb2.Session.Binding(
                preset_uid=binding.preset_uid,
                attr_uid=binding.attr_uid,
                required=binding.required,
            )
            for binding in session.bindings
        ),
    )


def build_method_message(method: AuthMethodMetadata) -> metadata_pb2.Method:
    """Internal: the message of a method."""
    return metadata_pb2.Method(
        name=method.name, sign_up=method.sign_up, sign_in=method.sign_in
    )
