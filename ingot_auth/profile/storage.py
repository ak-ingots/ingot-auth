"""The storage of the profiles."""

__all__ = ("AuthProfileStorage",)

from ingots.puer import Slot, Unit

from .attrs import BaseAuthAttrsStorage
from .tags import BaseAuthTagsStorage


class AuthProfileStorage(Unit):
    """The storage of the profiles, a registry a slot, each abstract."""

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    tags = Slot(BaseAuthTagsStorage)  # type: ignore[type-abstract]
    attrs = Slot(BaseAuthAttrsStorage)  # type: ignore[type-abstract]
