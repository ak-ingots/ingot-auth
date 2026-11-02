"""The items of the registries: what tags and attributes are declared with."""

__all__ = ("AuthAttrType", "AuthItem")

import enum
from dataclasses import dataclass


class AuthAttrType(enum.StrEnum):
    """The type of the values of an attribute, of a profile or of a session."""

    BOOL = "bool"
    INT = "int"
    DECIMAL = "decimal"
    DATETIME = "datetime"
    STR = "str"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthItem:
    """
    An item of a registry. ``id`` is what travels and what is stored: given
    explicitly, so it is the same in every environment, and never reused,
    even after its item is deleted. ``name`` is for people: it may change.
    """

    id: int
    name: str
