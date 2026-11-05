"""The storage of the sessions."""

__all__ = ("AuthSessionsStorage",)

from ingots.puer import Slot, Unit

from .attrs import BaseAuthSessionAttrsStorage
from .presets import BaseAuthSessionPresetsStorage


class AuthSessionsStorage(Unit):
    """The storage of the sessions, a registry a slot, each abstract."""

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    attrs = Slot(BaseAuthSessionAttrsStorage)  # type: ignore[type-abstract]
    presets = Slot(BaseAuthSessionPresetsStorage)  # type: ignore[type-abstract]
