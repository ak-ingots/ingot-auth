"""The servicer of the attributes of the sessions."""

__all__ = ("AuthGrpcSessionAttrsServicer",)

import typing as t

from ingot_auth.attrs import AuthAttrType
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.session_attrs import AuthSessionAttr, AuthSessionAttrSource

from ..proto.ingot_auth.v1 import session_attrs_pb2, session_attrs_pb2_grpc
from .base import BaseAuthGrpcServicer, Context

REGISTRY: t.Final = "session_attrs"
ATTR_TYPES: t.Final = {
    AuthAttrType.BOOL: session_attrs_pb2.ATTR_TYPE_BOOL,
    AuthAttrType.INT: session_attrs_pb2.ATTR_TYPE_INT,
    AuthAttrType.DECIMAL: session_attrs_pb2.ATTR_TYPE_DECIMAL,
    AuthAttrType.DATETIME: session_attrs_pb2.ATTR_TYPE_DATETIME,
    AuthAttrType.STR: session_attrs_pb2.ATTR_TYPE_STR,
}
ATTR_TYPES_BY_MESSAGE: t.Final = {value: key for key, value in ATTR_TYPES.items()}
SOURCES: t.Final = {
    AuthSessionAttrSource.TRANSPORT: session_attrs_pb2.SESSION_ATTR_SOURCE_TRANSPORT,
    AuthSessionAttrSource.CLIENT: session_attrs_pb2.SESSION_ATTR_SOURCE_CLIENT,
    AuthSessionAttrSource.PROVIDER: session_attrs_pb2.SESSION_ATTR_SOURCE_PROVIDER,
    AuthSessionAttrSource.DERIVED: session_attrs_pb2.SESSION_ATTR_SOURCE_DERIVED,
}
SOURCES_BY_MESSAGE: t.Final = {value: key for key, value in SOURCES.items()}


class AuthGrpcSessionAttrsServicer(
    BaseAuthGrpcServicer, session_attrs_pb2_grpc.SessionAttrsServicer
):
    """
    The attributes of the sessions for their administrator: its permissions
    come from :meth:`_get_caller`, which a subclass overrides, so an
    application serves this only to those it can tell apart.
    """

    @t.override
    async def Create(
        self, request: session_attrs_pb2.CreateSessionAttrRequest, context: Context
    ) -> session_attrs_pb2.CreateSessionAttrResponse:
        message = request.session_attr
        session_attr = AuthSessionAttr(
            id=message.id,
            name=message.name,
            type=build_attr_type(message.type),
            source=build_source(message.source),
        )
        factory = self.project.auth.session_attrs.op_create
        created = await self.run_operation(factory, session_attr, context)
        return session_attrs_pb2.CreateSessionAttrResponse(
            session_attr=build_session_attr_message(created)
        )

    @t.override
    async def List(
        self, request: session_attrs_pb2.ListSessionAttrsRequest, context: Context
    ) -> session_attrs_pb2.ListSessionAttrsResponse:
        factory = self.project.auth.session_attrs.op_list
        session_attrs = await self.run_operation(factory, None, context)
        return session_attrs_pb2.ListSessionAttrsResponse(
            session_attrs=map(build_session_attr_message, session_attrs)
        )

    @t.override
    async def Rename(
        self, request: session_attrs_pb2.RenameSessionAttrRequest, context: Context
    ) -> session_attrs_pb2.RenameSessionAttrResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.session_attrs.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return session_attrs_pb2.RenameSessionAttrResponse(
            session_attr=build_session_attr_message(renamed)
        )

    @t.override
    async def Delete(
        self, request: session_attrs_pb2.DeleteSessionAttrRequest, context: Context
    ) -> session_attrs_pb2.DeleteSessionAttrResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.session_attrs.op_delete
        await self.run_operation(factory, parameters, context)
        return session_attrs_pb2.DeleteSessionAttrResponse()


def build_session_attr_message(
    session_attr: AuthSessionAttr,
) -> session_attrs_pb2.SessionAttr:
    """Internal: the message of an attribute of the sessions."""
    return session_attrs_pb2.SessionAttr(
        id=session_attr.id,
        name=session_attr.name,
        type=ATTR_TYPES[session_attr.type],
        source=SOURCES[session_attr.source],
    )


def build_attr_type(
    message_type: session_attrs_pb2.AttrType.ValueType,
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
    message_source: session_attrs_pb2.SessionAttrSource.ValueType,
) -> AuthSessionAttrSource:
    """
    Internal: the source of an attribute of the sessions by its message.

    :raises AuthItemInvalidError: the source is not given, or not known.
    """
    try:
        return SOURCES_BY_MESSAGE[message_source]
    except KeyError:
        raise AuthItemInvalidError.for_source(REGISTRY, message_source) from None
