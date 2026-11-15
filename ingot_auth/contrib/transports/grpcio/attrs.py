"""The values of the attributes over gRPC, of the profiles and the sessions."""

__all__ = ("build_attr_value", "build_attr_value_message", "build_attr_values")

import datetime
import decimal
import typing as t

from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import AuthAttrValue

from ingot_auth.attrs.v1 import attrs_pb2

if t.TYPE_CHECKING:
    from collections.abc import Iterable


def build_attr_values(
    messages: "Iterable[attrs_pb2.AttrValue]", registry: str
) -> dict[int, AuthAttrValue]:
    """
    Internal: the values of the attributes of a registry a client gives, by
    the ids of their attributes; whether each is of the type of its attribute,
    and of the client, the core checks.

    :raises AuthItemInvalidError: a value is not given, a decimal is not one,
        or an attribute has two.
    """
    attr_values: dict[int, AuthAttrValue] = {}
    for message in messages:
        if message.attr_uid in attr_values:
            raise AuthItemInvalidError.for_value(registry, message.attr_uid)
        attr_values[message.attr_uid] = build_attr_value(message, registry)
    return attr_values


def build_attr_value(message: attrs_pb2.AttrValue, registry: str) -> AuthAttrValue:
    """
    Internal: the value of an attribute of a registry by its message.

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
                    registry, message.attr_uid
                ) from None
            if not value.is_finite():
                raise AuthItemInvalidError.for_value(registry, message.attr_uid)
            return value
        case "datetime_value":
            return message.datetime_value.ToDatetime(tzinfo=datetime.UTC)
        case "str_value":
            return message.str_value
    raise AuthItemInvalidError.for_value(registry, message.attr_uid)


def build_attr_value_message(
    attr_uid: int, value: AuthAttrValue
) -> attrs_pb2.AttrValue:
    """Internal: the message of the value of an attribute, of any registry."""
    message = attrs_pb2.AttrValue(attr_uid=attr_uid)
    if isinstance(value, bool):  # before int, a bool being one
        message.bool_value = value
    elif isinstance(value, int):
        message.int_value = value
    elif isinstance(value, decimal.Decimal):
        message.decimal_value = str(value)
    elif isinstance(value, datetime.datetime):
        message.datetime_value.FromDatetime(value)
    else:
        message.str_value = value
    return message
