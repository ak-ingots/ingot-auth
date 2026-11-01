"""The servicer of the metadata."""

__all__ = ("AuthGrpcMetadataServicer",)

import dataclasses
import typing as t

from ingots.defaults.operations import ANONYMOUS_CALLER, Caller, Permissions

from ingot_auth.attrs import AuthAttr, AuthAttrType
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.tags import AuthTag

from ..proto.ingot_auth.v1 import metadata_pb2, metadata_pb2_grpc
from .base import BaseAuthGrpcServicer, Context

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
            tags=map(build_tag_message, metadata.tags),
            attrs=map(build_attr_message, metadata.attrs),
        )

    @t.override
    def _get_caller(self, context: Context) -> Caller:
        return dataclasses.replace(
            ANONYMOUS_CALLER, permissions=Permissions(AuthMetadataPermissions.CAN_READ)
        )


def build_tag_message(tag: AuthTag) -> metadata_pb2.Tag:
    """Internal: the message of a tag."""
    return metadata_pb2.Tag(id=tag.id, name=tag.name)


def build_attr_message(attr: AuthAttr) -> metadata_pb2.Attr:
    """Internal: the message of an attribute."""
    return metadata_pb2.Attr(id=attr.id, name=attr.name, type=ATTR_TYPES[attr.type])
