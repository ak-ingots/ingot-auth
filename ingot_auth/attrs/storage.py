"""The storage of the attributes."""

__all__ = ("AuthMemoryAttrsStorage", "BaseAuthAttrsStorage")

import typing as t

from ingot_auth.registry import AuthMemoryRegistryStorage, BaseAuthRegistryStorage

from .items import AuthAttr


class BaseAuthAttrsStorage(BaseAuthRegistryStorage[AuthAttr]):
    """The storage of the attributes: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "attrs"


class AuthMemoryAttrsStorage(AuthMemoryRegistryStorage[AuthAttr], BaseAuthAttrsStorage):
    """The attributes in memory."""
