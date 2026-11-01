"""The servicer of the attributes."""

__all__ = ("AuthGrpcAttrsServicer",)

import typing as t

from ingot_auth.attrs import AuthAttr, AuthAttrType
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)

from ..proto.ingot_auth.v1 import attrs_pb2, attrs_pb2_grpc
from .base import BaseAuthGrpcServicer, Context

ATTR_TYPES: t.Final = {
    AuthAttrType.BOOL: attrs_pb2.ATTR_TYPE_BOOL,
    AuthAttrType.INT: attrs_pb2.ATTR_TYPE_INT,
    AuthAttrType.DECIMAL: attrs_pb2.ATTR_TYPE_DECIMAL,
    AuthAttrType.DATETIME: attrs_pb2.ATTR_TYPE_DATETIME,
    AuthAttrType.STR: attrs_pb2.ATTR_TYPE_STR,
}
ATTR_TYPES_BY_MESSAGE: t.Final = {value: key for key, value in ATTR_TYPES.items()}


class AuthGrpcAttrsServicer(BaseAuthGrpcServicer, attrs_pb2_grpc.AttrsServicer):
    """
    The attributes for their administrator: its permissions come from
    :meth:`_get_caller`, which a subclass overrides, so an application serves
    this only to those it can tell apart.
    """

    @t.override
    async def Create(
        self, request: attrs_pb2.CreateAttrRequest, context: Context
    ) -> attrs_pb2.CreateAttrResponse:
        message = request.attr
        attr = AuthAttr(
            id=message.id, name=message.name, type=build_attr_type(message.type)
        )
        factory = self.project.auth.attrs.op_create
        created = await self.run_operation(factory, attr, context)
        return attrs_pb2.CreateAttrResponse(attr=build_attr_message(created))

    @t.override
    async def List(
        self, request: attrs_pb2.ListAttrsRequest, context: Context
    ) -> attrs_pb2.ListAttrsResponse:
        attrs = await self.run_operation(self.project.auth.attrs.op_list, None, context)
        return attrs_pb2.ListAttrsResponse(attrs=map(build_attr_message, attrs))

    @t.override
    async def Rename(
        self, request: attrs_pb2.RenameAttrRequest, context: Context
    ) -> attrs_pb2.RenameAttrResponse:
        parameters = AuthRenameItemParameters(id=request.id, name=request.name)
        factory = self.project.auth.attrs.op_rename
        renamed = await self.run_operation(factory, parameters, context)
        return attrs_pb2.RenameAttrResponse(attr=build_attr_message(renamed))

    @t.override
    async def Delete(
        self, request: attrs_pb2.DeleteAttrRequest, context: Context
    ) -> attrs_pb2.DeleteAttrResponse:
        parameters = AuthDeleteItemParameters(id=request.id)
        factory = self.project.auth.attrs.op_delete
        await self.run_operation(factory, parameters, context)
        return attrs_pb2.DeleteAttrResponse()


def build_attr_message(attr: AuthAttr) -> attrs_pb2.Attr:
    """Internal: the message of an attribute."""
    return attrs_pb2.Attr(id=attr.id, name=attr.name, type=ATTR_TYPES[attr.type])


def build_attr_type(message_type: attrs_pb2.AttrType.ValueType) -> AuthAttrType:
    """
    Internal: the type of an attribute by its message.

    :raises AuthItemInvalidError: the type is not given, or not known.
    """
    try:
        return ATTR_TYPES_BY_MESSAGE[message_type]
    except KeyError:
        raise AuthItemInvalidError.for_type("attrs", message_type) from None
