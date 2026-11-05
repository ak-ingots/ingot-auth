"""The storage of the sessions in memory."""

__all__ = (
    "AuthMemorySessionAttrsStorage",
    "AuthMemorySessionPresetsStorage",
    "AuthMemorySessionsStorage",
)

from ingots.puer import Slot

from ingot_auth.sessions import AuthSessionsStorage

from .attrs import AuthMemorySessionAttrsStorage
from .presets import AuthMemorySessionPresetsStorage


class AuthMemorySessionsStorage(AuthSessionsStorage):
    """The storage of the sessions in memory."""

    attrs = Slot(AuthMemorySessionAttrsStorage)
    presets = Slot(AuthMemorySessionPresetsStorage)
