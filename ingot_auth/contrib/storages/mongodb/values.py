"""The values of the attributes in MongoDB, shared by the storages keeping them."""

__all__ = ("build_bson_values", "build_values")

import decimal
import typing as t

from bson.decimal128 import Decimal128

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue

    from .collection import Document


def build_bson_values(values: "Mapping[int, AuthAttrValue]") -> "list[Document]":
    """
    The values of the attributes for a document: a list of the ids of their
    attributes with them, as a key of a document is a string; a decimal is a
    ``Decimal128`` of BSON, the other types are those of BSON already.
    """
    return [
        {"attr_id": attr_id, "value": _build_bson_value(value)}
        for attr_id, value in values.items()
    ]


def build_values(documents: "list[Document]") -> "dict[int, AuthAttrValue]":
    """The values of the attributes from a document, as given to it."""
    return {bound["attr_id"]: _build_value(bound["value"]) for bound in documents}


def _build_bson_value(value: "AuthAttrValue") -> object:
    return Decimal128(value) if isinstance(value, decimal.Decimal) else value


def _build_value(value: object) -> "AuthAttrValue":
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return t.cast("AuthAttrValue", value)
