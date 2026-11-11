"""
The items of the registries, what the tags and the attributes are declared
with, and the types of the values of the attributes.
"""

__all__ = ("ATTR_VALUE_TYPES", "AuthAttrType", "AuthAttrValue", "AuthItem")

import datetime
import decimal
import enum
import typing as t
from dataclasses import dataclass


class AuthAttrType(enum.StrEnum):
    """The type of the values of an attribute, of a profile or of a session."""

    BOOL = "bool"
    INT = "int"
    DECIMAL = "decimal"
    DATETIME = "datetime"
    STR = "str"


AuthAttrValue: t.TypeAlias = bool | int | decimal.Decimal | datetime.datetime | str
"""A value of an attribute: of one of the types of :class:`AuthAttrType`."""

# the class of the values of each type: exactly, a bool is not an int here
ATTR_VALUE_TYPES: t.Final[dict[AuthAttrType, type]] = {
    AuthAttrType.BOOL: bool,
    AuthAttrType.INT: int,
    AuthAttrType.DECIMAL: decimal.Decimal,
    AuthAttrType.DATETIME: datetime.datetime,
    AuthAttrType.STR: str,
}


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthItem:
    """
    An item of a registry. ``id`` is what travels and what is stored: given
    explicitly, so it is the same in every environment, and never reused,
    even after its item is deleted. ``name`` is for people: it may change.
    """

    id: int
    name: str
