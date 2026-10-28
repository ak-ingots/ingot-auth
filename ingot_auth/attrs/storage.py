"""The storage of the attributes."""

__all__ = ("BaseAuthAttrsStorage",)

import typing as t

from ingot_auth.registry import BaseAuthRegistryStorage

from .items import AuthAttr


class BaseAuthAttrsStorage(BaseAuthRegistryStorage[AuthAttr]):
    """The storage of the attributes: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "attrs"
