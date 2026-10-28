"""The attribute: a typed value of a profile."""

__all__ = ("AuthAttr", "AuthAttrType")

import enum
from dataclasses import dataclass

from ingot_auth.registry import AuthItem


class AuthAttrType(enum.StrEnum):
    """The type of the values of an attribute."""

    BOOL = "bool"
    INT = "int"
    DECIMAL = "decimal"
    DATETIME = "datetime"
    STR = "str"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttr(AuthItem):
    """
    An attribute of the profiles: ``first_name``, ``title/en``. Its type is
    given once: renaming keeps it, and nothing changes it.
    """

    type: AuthAttrType
