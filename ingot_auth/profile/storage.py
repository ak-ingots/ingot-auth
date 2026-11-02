"""The storage of the profiles."""

__all__ = ("AuthProfileStorage",)

from ingots.puer import Slot, Unit

from .attrs import BaseAuthAttrsStorage
from .identities import BaseAuthIdentitiesStorage
from .profiles import BaseAuthProfilesStorage
from .tags import BaseAuthTagsStorage


class AuthProfileStorage(Unit):
    """
    The storage of the profiles: the registries, the profiles and their
    identities, each abstract.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    tags = Slot(BaseAuthTagsStorage)  # type: ignore[type-abstract]
    attrs = Slot(BaseAuthAttrsStorage)  # type: ignore[type-abstract]
    profiles = Slot(BaseAuthProfilesStorage)  # type: ignore[type-abstract]
    identities = Slot(BaseAuthIdentitiesStorage)  # type: ignore[type-abstract]
