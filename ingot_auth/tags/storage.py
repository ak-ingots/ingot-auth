"""The storage of the tags."""

__all__ = ("BaseAuthTagsStorage",)

import typing as t

from ingot_auth.registry import BaseAuthRegistryStorage

from .items import AuthTag


class BaseAuthTagsStorage(BaseAuthRegistryStorage[AuthTag]):
    """The storage of the tags: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "tags"
