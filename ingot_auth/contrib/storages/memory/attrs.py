"""The attributes in memory."""

__all__ = ("AuthMemoryAttrsStorage",)

from ingot_auth.attrs import AuthAttr, BaseAuthAttrsStorage

from .registry import AuthMemoryRegistryStorage


class AuthMemoryAttrsStorage(AuthMemoryRegistryStorage[AuthAttr], BaseAuthAttrsStorage):
    """The attributes in memory."""
