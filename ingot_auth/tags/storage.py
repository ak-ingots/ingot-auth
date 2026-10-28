"""The storage of the tags."""

__all__ = ("AuthMemoryTagsStorage", "BaseAuthTagsStorage")

import typing as t

from ingot_auth.registry import AuthMemoryRegistryStorage, BaseAuthRegistryStorage

from .items import AuthTag


class BaseAuthTagsStorage(BaseAuthRegistryStorage[AuthTag]):
    """The storage of the tags: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "tags"


class AuthMemoryTagsStorage(AuthMemoryRegistryStorage[AuthTag], BaseAuthTagsStorage):
    """The tags in memory."""
