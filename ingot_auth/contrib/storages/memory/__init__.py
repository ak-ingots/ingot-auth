"""
The storage in memory: for the tests and the addon run on its own. What it
stores is gone with the project. An application declares it in the slot of
its auth: ``storage = Slot(AuthMemoryStorage)``.
"""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryIdentitiesStorage",
    "AuthMemoryProfilesStorage",
    "AuthMemoryRegistryStorage",
    "AuthMemorySecretsStorage",
    "AuthMemorySessionAttrsStorage",
    "AuthMemorySessionPresetsStorage",
    "AuthMemorySessionsStorage",
    "AuthMemorySignUpRecordsStorage",
    "AuthMemorySignUpStorage",
    "AuthMemoryStateMixin",
    "AuthMemoryStorage",
    "AuthMemoryTagsStorage",
)

import typing as t

from ingots.puer import Slot

from ingot_auth.storage import AuthStorage

from .profiles import (
    AuthMemoryAttrsStorage,
    AuthMemoryIdentitiesStorage,
    AuthMemoryProfilesStorage,
    AuthMemorySecretsStorage,
    AuthMemoryTagsStorage,
)
from .registry import AuthMemoryRegistryStorage
from .sessions import (
    AuthMemorySessionAttrsStorage,
    AuthMemorySessionPresetsStorage,
    AuthMemorySessionsStorage,
)
from .sign_up import AuthMemorySignUpRecordsStorage, AuthMemorySignUpStorage
from .state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from collections.abc import Iterator


class AuthMemoryStorage(AuthStorage):
    """
    The storage of the auth in memory. A transaction copies every storage
    when it begins and puts the copies back when it is rolled back: it
    isolates nothing, so a rollback undoes what other tasks wrote meanwhile
    too. For the tests and a project of one task at a time.
    """

    profiles = Slot(AuthMemoryProfilesStorage)
    sessions = Slot(AuthMemorySessionsStorage)
    sign_up = Slot(AuthMemorySignUpStorage)

    @t.override
    async def _begin(self) -> object:
        return {path: entity._memory_save() for path, entity in self._iter_states()}

    @t.override
    async def _commit(self, transaction: object) -> None:
        pass

    @t.override
    async def _rollback(self, transaction: object) -> None:
        states = t.cast(dict[str, dict[str, object]], transaction)
        for path, entity in self._iter_states():
            entity._memory_restore(states[path])

    def _iter_states(self) -> "Iterator[tuple[str, AuthMemoryStateMixin]]":
        """Every storage of the backend, created on the way, with its path."""
        for path, slot in type(self).slots_walk():
            if issubclass(slot.cls, AuthMemoryStateMixin):
                entity = self.slots_find_entity(path)
                yield path, t.cast(AuthMemoryStateMixin, entity)
