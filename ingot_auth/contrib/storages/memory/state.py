"""The state of a storage in memory, which the transactions copy and put back."""

__all__ = ("AuthMemoryStateMixin",)

import copy
import typing as t

from ingots.puer import Entity

# the attribute of an entity holding its project, never copied
PROJECT_REF: t.Final = "_project_ref"


class AuthMemoryStateMixin:
    """
    A storage in memory: what a transaction of :class:`AuthMemoryStorage`
    copies when it begins and puts back when it is rolled back is every
    attribute of the storage but its project and the entities of its slots,
    each a storage of its own.
    """

    @t.final
    def _memory_save(self) -> dict[str, object]:
        return {
            name: copy.deepcopy(value)
            for name, value in vars(self).items()
            if name != PROJECT_REF and not isinstance(value, Entity)
        }

    @t.final
    def _memory_restore(self, state: dict[str, object]) -> None:
        vars(self).update(state)
