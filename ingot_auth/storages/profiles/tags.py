"""The storage of the tags."""

__all__ = ("BaseAuthTagsStorage",)

import typing as t

from ..registry import BaseAuthRegistryStorage
from .data import AuthTag


class BaseAuthTagsStorage(BaseAuthRegistryStorage[AuthTag]):
    """The storage of the tags: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "profiles.tags"
