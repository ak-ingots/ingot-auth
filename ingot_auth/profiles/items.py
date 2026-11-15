"""
The parameters of the operations of the values of the profiles, and what a
client sees of the profile of its caller.
"""

__all__ = (
    "AuthOwnProfile",
    "AuthSetProfileAttrValuesParameters",
    "AuthSetProfileTagsParameters",
)

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSetProfileTagsParameters:
    """The uid of a profile and the ids of all the tags it is to have."""

    uid: str
    tag_ids: frozenset[int]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSetProfileAttrValuesParameters:
    """
    The uid of a profile and all the values of its attributes it is to have,
    by the ids of the attributes.
    """

    uid: str
    attr_values: "Mapping[int, AuthAttrValue]"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthOwnProfile:
    """
    The profile of the caller as its client sees it, to build its interface:
    the ids of its tags, the values of its attributes by their ids, its
    permissions, a mask per domain, and the hash of them all, which every
    reply tells, so that the client knows when to ask again.
    """

    tag_ids: frozenset[int]
    attr_values: "Mapping[int, AuthAttrValue]"
    permissions: "Mapping[str, int]"
    hash: str
