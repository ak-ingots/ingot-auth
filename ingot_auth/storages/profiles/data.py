"""
What the storage of the profiles keeps: the profiles, their identities, and
the items of the registries of their tags and attributes.
"""

__all__ = ("AuthAttr", "AuthIdentity", "AuthProfile", "AuthProfileValues", "AuthTag")

import datetime
import typing as t
from dataclasses import dataclass, field

from ..data import AuthAttrType, AuthItem

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ..data import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfile:
    """
    A profile: ``uid`` is what the rest of an application knows the user by.
    The values of its tags and attributes are kept apart,
    :class:`AuthProfileValues`.
    """

    uid: str
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfileValues:
    """
    The values of a profile: the ids of the tags it has, and the values of
    its attributes, by the ids of the attributes; empty for a profile of none.
    """

    tag_uids: frozenset[int] = frozenset()
    attr_values: "Mapping[int, AuthAttrValue]" = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthIdentity:
    """An identifier of a kind, bound to a profile: unique within its kind."""

    kind: str
    value: str
    profile_uid: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthTag(AuthItem):
    """
    A tag of the profiles: ``beta``, ``staff``. A mark, not a permission:
    the permissions of a caller decide what it may do.
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttr(AuthItem):
    """
    An attribute of the profiles: ``first_name``, ``title/en``. Its type is
    given once: renaming keeps it, and nothing changes it.
    """

    type: AuthAttrType
