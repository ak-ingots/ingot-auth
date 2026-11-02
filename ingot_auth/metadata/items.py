"""The metadata: what the consumers of the auth need to read a profile."""

__all__ = ("AuthMetadata",)

from dataclasses import dataclass

from ingot_auth.profile.attrs import AuthAttr
from ingot_auth.profile.tags import AuthTag


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthMetadata:
    """The registries as a whole: the ids a profile holds, with their names."""

    tags: tuple[AuthTag, ...]
    attrs: tuple[AuthAttr, ...]
