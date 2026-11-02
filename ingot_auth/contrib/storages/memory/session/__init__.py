"""The storage of the sessions in memory."""

__all__ = ("AuthMemorySessionAttrsStorage", "AuthMemorySessionStorage")

from ingots.puer import Slot

from ingot_auth.session import AuthSessionStorage

from .attrs import AuthMemorySessionAttrsStorage


class AuthMemorySessionStorage(AuthSessionStorage):
    """The storage of the sessions in memory."""

    attrs = Slot(AuthMemorySessionAttrsStorage)
