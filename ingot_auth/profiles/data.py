"""What a client sees of the profile of its caller."""

__all__ = ("AuthOwnProfile",)

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthOwnProfile:
    """
    The profile of the caller as its client sees it, to build its interface:
    the ids of its tags, the values of its attributes by their ids, its
    permissions, a mask per domain, and the hash of them all, which every
    reply tells, so that the client knows when to ask again.
    """

    tag_uids: frozenset[int]
    attr_values: "Mapping[int, AuthAttrValue]"
    permissions: "Mapping[str, int]"
    hash: str
