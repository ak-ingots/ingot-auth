"""The storage of the sessions in MongoDB."""

__all__ = (
    "AuthMongoDbSessionAttrsStorage",
    "AuthMongoDbSessionPresetsStorage",
    "AuthMongoDbSessionStorage",
)

from ingots.puer import Slot

from ingot_auth.session import AuthSessionStorage

from .attrs import AuthMongoDbSessionAttrsStorage
from .presets import AuthMongoDbSessionPresetsStorage


class AuthMongoDbSessionStorage(AuthSessionStorage):
    """The storage of the sessions in MongoDB."""

    attrs = Slot(AuthMongoDbSessionAttrsStorage)
    presets = Slot(AuthMongoDbSessionPresetsStorage)
