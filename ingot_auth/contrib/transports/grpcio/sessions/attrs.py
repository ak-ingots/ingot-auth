"""The servicer of the attributes of the sessions."""

__all__ = ("AuthGrpcSessionAttrsServicer",)

import datetime
import decimal
import typing as t

from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.storages import (
    AuthAttrType,
    AuthAttrValue,
    AuthSessionAttr,
    AuthSessionAttrSource,
)

from ..base import BaseAuthGrpcServicer, Context
from ingot_auth.sessions.attrs.v1 import attrs_pb2, attrs_pb2_grpc

if t.TYPE_CHECKING:
    from collections.abc import Iterable

REGISTRY: t.Final = "sessions.attrs"
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
    are those of the session of the token of the call, by
    :meth:`_get_caller`.
    """

    @t.override
    async def CreateAttr(
        self, request: attrs_pb2.CreateAttrRequest, context: Context
    ) -> attrs_pb2.CreateAttrResponse:
        message = request.attr
        session_attr = AuthSessionAttr(
            id=message.id,
            name=message.name,
            type=build_attr_type(message.type),
            source=build_source(message.source),
        )
        factory = self.project.auth.sessions.attrs.op_create
        created = await self.run_operation(factory, session_attr, context)
        return attrs_pb2.CreateAttrResponse(attr=build_session_attr_message(created))

    @t.override
    async def ListAttrs(
        self, request: attrs_pb2.ListAttrsRequest, context: Context
    ) -> attrs_pb2.ListAttrsResponse:
        factory = self.project.auth.sessions.attrs.op_list
        session_attrs = await self.run_operation(factory, None, context)
        return attrs_pb2.ListAttrsResponse(
            attrs=map(build_session_attr_message, session_attrs)
        )

    @t.override
    async def RenameAttr(
        self, request: attrs_pb2.RenameAttrRequest, context: Context
    ) -> attrs_pb2.RenameAttrResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.sessions.attrs.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return attrs_pb2.RenameAttrResponse(attr=build_session_attr_message(renamed))

    @t.override
    async def DeleteAttr(
        self, request: attrs_pb2.DeleteAttrRequest, context: Context
    ) -> attrs_pb2.DeleteAttrResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.sessions.attrs.op_delete
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


def build_attr_values(
    messages: "Iterable[attrs_pb2.AttrValue]",
) -> dict[int, AuthAttrValue]:
    """
    Internal: the values of the attributes of the sessions a client gives, by
    the ids of their attributes; whether each is of the type of its attribute,
    and of the client, the core checks.

    :raises AuthItemInvalidError: a value is not given, a decimal is not one,
        or an attribute has two.
    """
    attr_values: dict[int, AuthAttrValue] = {}
    for message in messages:
        if message.attr_id in attr_values:
            raise AuthItemInvalidError.for_value(REGISTRY, message.attr_id)
        attr_values[message.attr_id] = build_attr_value(message)
    return attr_values


def build_attr_value(message: attrs_pb2.AttrValue) -> AuthAttrValue:
    """
    Internal: the value of an attribute of the sessions by its message.

    :raises AuthItemInvalidError: no value is given, or a decimal is not one.
    """
    match message.WhichOneof("value"):
        case "bool_value":
            return message.bool_value
        case "int_value":
            return message.int_value
        case "decimal_value":
            try:
                value = decimal.Decimal(message.decimal_value)
            except decimal.InvalidOperation:
                raise AuthItemInvalidError.for_value(
                    REGISTRY, message.attr_id
                ) from None
            if not value.is_finite():
                raise AuthItemInvalidError.for_value(REGISTRY, message.attr_id)
            return value
        case "datetime_value":
            return message.datetime_value.ToDatetime(tzinfo=datetime.UTC)
        case "str_value":
            return message.str_value
    raise AuthItemInvalidError.for_value(REGISTRY, message.attr_id)
