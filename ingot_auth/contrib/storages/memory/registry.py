"""A registry in memory."""

__all__ = ("AuthMemoryRegistryStorage",)

import dataclasses
import typing as t

from ingot_auth.registry import (
    AuthItem,
    AuthItemConflictError,
    AuthItemNotFoundError,
    BaseAuthRegistryStorage,
)

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryRegistryStorage[ItemType: AuthItem](BaseAuthRegistryStorage[ItemType]):
    """
    A registry in memory, for the tests and the addon run on its own: gone
    with the project.
    """

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._items: dict[int, ItemType] = {}
        self._taken_ids: set[int] = set()

    @t.override
    async def _create(self, item: ItemType) -> None:
        if item.id in self._taken_ids:
            raise AuthItemConflictError.for_id(self.REGISTRY, item.id)
        self._check_name(item.name)
        self._items[item.id] = item
        self._taken_ids.add(item.id)

    @t.override
    async def _get_all(self) -> tuple[ItemType, ...]:
        return tuple(self._items[item_id] for item_id in sorted(self._items))

    @t.override
    async def _rename(self, item_id: int, name: str) -> ItemType:
        item = self._get(item_id)
        if name != item.name:
            self._check_name(name)
        self._items[item_id] = item = dataclasses.replace(item, name=name)
        return item

    @t.override
    async def _delete(self, item_id: int) -> None:
        self._get(item_id)
        del self._items[item_id]

    def _get(self, item_id: int) -> ItemType:
        try:
            return self._items[item_id]
        except KeyError:
            raise AuthItemNotFoundError.for_id(self.REGISTRY, item_id) from None

    def _check_name(self, name: str) -> None:
        if any(item.name == name for item in self._items.values()):
            raise AuthItemConflictError.for_name(self.REGISTRY, name)
