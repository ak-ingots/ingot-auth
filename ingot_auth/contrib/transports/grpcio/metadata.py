"""The metadata over gRPC: its servicer and its binding."""

__all__ = ("AuthGrpcMetadataBinding", "AuthGrpcMetadataServicer")

import dataclasses
import typing as t

from ingot_grpcio.grpc.services import GrpcService
from ingots.defaults.operations import ANONYMOUS_CALLER, Caller, Permissions

from ingot_auth.metadata import (
    AuthMetadataPermissions,
    AuthProfileMetadata,
    AuthSessionMetadata,
)
from ingot_auth.registry import AuthAttrType

from .base import BaseAuthGrpcServicer, Context
from .proto.ingot_auth.metadata.v1 import metadata_pb2, metadata_pb2_grpc

ATTR_TYPES: t.Final = {
    AuthAttrType.BOOL: metadata_pb2.ATTR_TYPE_BOOL,
    AuthAttrType.INT: metadata_pb2.ATTR_TYPE_INT,
    AuthAttrType.DECIMAL: metadata_pb2.ATTR_TYPE_DECIMAL,
    AuthAttrType.DATETIME: metadata_pb2.ATTR_TYPE_DATETIME,
    AuthAttrType.STR: metadata_pb2.ATTR_TYPE_STR,
}


class AuthGrpcMetadataServicer(
    BaseAuthGrpcServicer, metadata_pb2_grpc.MetadataServicer
):
    """
    The metadata, public unless told otherwise: a client asks for it before
    signing in, so anyone may read it until a subclass overrides
    :meth:`_get_caller`.
    """

    @t.override
    async def Get(
        self, request: metadata_pb2.GetMetadataRequest, context: Context
    ) -> metadata_pb2.GetMetadataResponse:
        metadata = await self.run_operation(
            self.project.auth.metadata.op_get, None, context
        )
        return metadata_pb2.GetMetadataResponse(
            profile=build_profile_message(metadata.profile),
            session=build_session_message(metadata.session),
        )

    @t.override
    def _get_caller(self, context: Context) -> Caller:
        return dataclasses.replace(
            ANONYMOUS_CALLER, permissions=Permissions(AuthMetadataPermissions.CAN_READ)
        )


class AuthGrpcMetadataBinding:
    auth_metadata = GrpcService(
        metadata_pb2_grpc.MetadataStub, AuthGrpcMetadataServicer
    )


def build_profile_message(profile: AuthProfileMetadata) -> metadata_pb2.Profile:
    """Internal: the message of the metadata of the profiles."""
    return metadata_pb2.Profile(
        tags=(
            metadata_pb2.Profile.Tag(id=tag.id, name=tag.name) for tag in profile.tags
        ),
        attrs=(
            metadata_pb2.Profile.Attr(
                id=attr.id, name=attr.name, type=ATTR_TYPES[attr.type]
            )
            for attr in profile.attrs
        ),
    )


def build_session_message(session: AuthSessionMetadata) -> metadata_pb2.Session:
    """Internal: the message of the metadata of the sessions."""
    return metadata_pb2.Session(
        attrs=(
            metadata_pb2.Session.Attr(
                id=attr.id, name=attr.name, type=ATTR_TYPES[attr.type]
            )
            for attr in session.attrs
        ),
        presets=(
            metadata_pb2.Session.Preset(id=preset.id, name=preset.name)
            for preset in session.presets
        ),
        bindings=(
            metadata_pb2.Session.Binding(
                preset_id=binding.preset_id,
                attr_id=binding.attr_id,
                required=binding.required,
            )
            for binding in session.bindings
        ),
    )
