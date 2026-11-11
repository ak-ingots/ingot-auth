"""The storage of the attributes of the sessions."""

__all__ = ("BaseAuthSessionAttrsStorage",)

import typing as t

from ..registry import BaseAuthRegistryStorage
from .items import AuthSessionAttr


class BaseAuthSessionAttrsStorage(BaseAuthRegistryStorage[AuthSessionAttr]):
    """The storage of the attributes of the sessions: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "sessions.attrs"
