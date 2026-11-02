"""The storage of the attributes of the sessions."""

__all__ = ("BaseAuthSessionAttrsStorage",)

import typing as t

from ingot_auth.registry import BaseAuthRegistryStorage

from .items import AuthSessionAttr


class BaseAuthSessionAttrsStorage(BaseAuthRegistryStorage[AuthSessionAttr]):
    """The storage of the attributes of the sessions: what a backend implements."""

    REGISTRY: t.ClassVar[str] = "session_attrs"
