"""The parameters of the operations of the values of the profiles."""

__all__ = ("AuthSetProfileAttrValuesParameters", "AuthSetProfileTagsParameters")

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
