"""The storage of the sessions."""

__all__ = ("AuthSessionStorage",)

from ingots.puer import Slot, Unit

from .attrs import BaseAuthSessionAttrsStorage


class AuthSessionStorage(Unit):
    """The storage of the sessions, a registry a slot, each abstract."""

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    attrs = Slot(BaseAuthSessionAttrsStorage)  # type: ignore[type-abstract]
