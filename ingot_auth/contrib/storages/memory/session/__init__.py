"""The storage of the sessions in memory."""

__all__ = (
    "AuthMemorySessionAttrsStorage",
    "AuthMemorySessionPresetsStorage",
    "AuthMemorySessionStorage",
)

from ingots.puer import Slot

from ingot_auth.session import AuthSessionStorage

from .attrs import AuthMemorySessionAttrsStorage
from .presets import AuthMemorySessionPresetsStorage


class AuthMemorySessionStorage(AuthSessionStorage):
    """The storage of the sessions in memory."""

    attrs = Slot(AuthMemorySessionAttrsStorage)
    presets = Slot(AuthMemorySessionPresetsStorage)
