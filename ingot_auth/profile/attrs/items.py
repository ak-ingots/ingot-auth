"""The attribute: a typed value of a profile."""

__all__ = ("AuthAttr",)

from dataclasses import dataclass

from ingot_auth.registry import AuthAttrType, AuthItem


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttr(AuthItem):
    """
    An attribute of the profiles: ``first_name``, ``title/en``. Its type is
    given once: renaming keeps it, and nothing changes it.
    """

    type: AuthAttrType
