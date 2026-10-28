"""
The storage of the auth: a facade, one storage a registry, which a backend
implements; :class:`AuthMemoryStorage` keeps everything in memory.
"""

__all__ = ("AuthMemoryStorage", "AuthStorage")

from ingots.puer import Slot, Unit

from ingot_auth.attrs import AuthMemoryAttrsStorage, BaseAuthAttrsStorage
from ingot_auth.tags import AuthMemoryTagsStorage, BaseAuthTagsStorage


class AuthStorage(Unit):
    """
    The storage of the auth, every part of it abstract: a backend extends
    it with its own, and the project declares it in the slot of the auth.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    tags = Slot(BaseAuthTagsStorage)  # type: ignore[type-abstract]
    attrs = Slot(BaseAuthAttrsStorage)  # type: ignore[type-abstract]


class AuthMemoryStorage(AuthStorage):
    """The storage in memory: for the tests and the addon run on its own."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)
