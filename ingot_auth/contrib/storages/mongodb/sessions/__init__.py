"""The storage of the sessions in MongoDB."""

__all__ = (
    "AuthMongoDbSessionAttrsStorage",
    "AuthMongoDbSessionPresetsStorage",
    "AuthMongoDbSessionsStorage",
)

from ingots.puer import Slot

from ingot_auth.sessions import AuthSessionsStorage

from .attrs import AuthMongoDbSessionAttrsStorage
from .presets import AuthMongoDbSessionPresetsStorage


class AuthMongoDbSessionsStorage(AuthSessionsStorage):
    """The storage of the sessions in MongoDB."""

    attrs = Slot(AuthMongoDbSessionAttrsStorage)
    presets = Slot(AuthMongoDbSessionPresetsStorage)
