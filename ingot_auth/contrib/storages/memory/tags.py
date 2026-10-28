"""The tags in memory."""

__all__ = ("AuthMemoryTagsStorage",)

from ingot_auth.tags import AuthTag, BaseAuthTagsStorage

from .registry import AuthMemoryRegistryStorage


class AuthMemoryTagsStorage(AuthMemoryRegistryStorage[AuthTag], BaseAuthTagsStorage):
    """The tags in memory."""
