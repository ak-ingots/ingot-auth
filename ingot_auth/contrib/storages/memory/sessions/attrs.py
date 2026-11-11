"""The attributes of the sessions in memory."""

__all__ = ("AuthMemorySessionAttrsStorage",)

from ingot_auth.storages import AuthSessionAttr, BaseAuthSessionAttrsStorage

from ..registry import AuthMemoryRegistryStorage


class AuthMemorySessionAttrsStorage(
    AuthMemoryRegistryStorage[AuthSessionAttr], BaseAuthSessionAttrsStorage
):
    """The attributes of the sessions in memory."""
