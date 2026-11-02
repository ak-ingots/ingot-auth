"""The servicer of the attributes of the sessions."""

__all__ = ("AuthGrpcSessionAttrsServicer",)

import typing as t

from ingot_auth.registry import AuthAttrType, AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.session.attrs import AuthSessionAttr, AuthSessionAttrSource

from ..base import BaseAuthGrpcServicer, Context
from ..proto.ingot_auth.session.attrs.v1 import attrs_pb2, attrs_pb2_grpc

REGISTRY: t.Final = "session.attrs"
ATTR_TYPES: t.Final = {
    AuthAttrType.BOOL: attrs_pb2.ATTR_TYPE_BOOL,
    AuthAttrType.INT: attrs_pb2.ATTR_TYPE_INT,
    AuthAttrType.DECIMAL: attrs_pb2.ATTR_TYPE_DECIMAL,
    AuthAttrType.DATETIME: attrs_pb2.ATTR_TYPE_DATETIME,
    AuthAttrType.STR: attrs_pb2.ATTR_TYPE_STR,
}
ATTR_TYPES_BY_MESSAGE: t.Final = {value: key for key, value in ATTR_TYPES.items()}
SOURCES: t.Final = {
    AuthSessionAttrSource.TRANSPORT: attrs_pb2.ATTR_SOURCE_TRANSPORT,
    AuthSessionAttrSource.CLIENT: attrs_pb2.ATTR_SOURCE_CLIENT,
    AuthSessionAttrSource.PROVIDER: attrs_pb2.ATTR_SOURCE_PROVIDER,
    AuthSessionAttrSource.DERIVED: attrs_pb2.ATTR_SOURCE_DERIVED,
}
SOURCES_BY_MESSAGE: t.Final = {value: key for key, value in SOURCES.items()}


class AuthGrpcSessionAttrsServicer(BaseAuthGrpcServicer, attrs_pb2_grpc.AttrsServicer):
    """
    The attributes of the sessions for their administrator: its permissions
    come from :meth:`_get_caller`, which a subclass overrides, so an
    application serves this only to those it can tell apart.
    """

    @t.override
    async def Create(
        self, request: attrs_pb2.CreateAttrRequest, context: Context
    ) -> attrs_pb2.CreateAttrResponse:
        message = request.attr
        session_attr = AuthSessionAttr(
            id=message.id,
            name=message.name,
            type=build_attr_type(message.type),
            source=build_source(message.source),
        )
        factory = self.project.auth.session.attrs.op_create
        created = await self.run_operation(factory, session_attr, context)
        return attrs_pb2.CreateAttrResponse(attr=build_session_attr_message(created))

    @t.override
    async def List(
        self, request: attrs_pb2.ListAttrsRequest, context: Context
    ) -> attrs_pb2.ListAttrsResponse:
        factory = self.project.auth.session.attrs.op_list
        session_attrs = await self.run_operation(factory, None, context)
        return attrs_pb2.ListAttrsResponse(
            attrs=map(build_session_attr_message, session_attrs)
        )

    @t.override
    async def Rename(
        self, request: attrs_pb2.RenameAttrRequest, context: Context
    ) -> attrs_pb2.RenameAttrResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.session.attrs.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return attrs_pb2.RenameAttrResponse(attr=build_session_attr_message(renamed))

    @t.override
    async def Delete(
        self, request: attrs_pb2.DeleteAttrRequest, context: Context
    ) -> attrs_pb2.DeleteAttrResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.session.attrs.op_delete
        await self.run_operation(factory, parameters, context)
        return attrs_pb2.DeleteAttrResponse()


def build_session_attr_message(
    session_attr: AuthSessionAttr,
) -> attrs_pb2.Attr:
    """Internal: the message of an attribute of the sessions."""
    return attrs_pb2.Attr(
        id=session_attr.id,
        name=session_attr.name,
        type=ATTR_TYPES[session_attr.type],
        source=SOURCES[session_attr.source],
    )


def build_attr_type(
    message_type: attrs_pb2.AttrType.ValueType,
) -> AuthAttrType:
    """
    Internal: the type of an attribute of the sessions by its message.

    :raises AuthItemInvalidError: the type is not given, or not known.
    """
    try:
        return ATTR_TYPES_BY_MESSAGE[message_type]
    except KeyError:
        raise AuthItemInvalidError.for_type(REGISTRY, message_type) from None


def build_source(
    message_source: attrs_pb2.AttrSource.ValueType,
) -> AuthSessionAttrSource:
    """
    Internal: the source of an attribute of the sessions by its message.

    :raises AuthItemInvalidError: the source is not given, or not known.
    """
    try:
        return SOURCES_BY_MESSAGE[message_source]
    except KeyError:
        raise AuthItemInvalidError.for_source(REGISTRY, message_source) from None
