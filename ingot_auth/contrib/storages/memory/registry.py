"""A registry in memory."""

__all__ = ("AuthMemoryRegistryStorage",)

import dataclasses
import typing as t

from ingot_auth.storages import (
    AuthItem,
    AuthItemConflictError,
    AuthItemNotFoundError,
    BaseAuthRegistryStorage,
)

from .state import AuthMemoryStateMixin


class AuthMemoryRegistryStorage[ItemType: AuthItem](
    AuthMemoryStateMixin, BaseAuthRegistryStorage[ItemType]
):
    """
    A registry in memory, for the tests and the addon run on its own: gone
    with the project.
    """

    def __init__(self) -> None:
        super().__init__()
        self._items: dict[int, ItemType] = {}
        self._taken_ids: set[int] = set()

    @t.override
    async def _create(self, item: ItemType) -> None:
        if item.uid in self._taken_ids:
            raise AuthItemConflictError.for_uid(self.REGISTRY, item.uid)
        self._check_name(item.name)
        self._items[item.uid] = item
        self._taken_ids.add(item.uid)

    @t.override
    async def _get_all(self) -> tuple[ItemType, ...]:
        return tuple(self._items[item_uid] for item_uid in sorted(self._items))

    @t.override
    async def _rename(self, item_uid: int, name: str) -> ItemType:
        item = self._get(item_uid)
        if name != item.name:
            self._check_name(name)
        self._items[item_uid] = item = dataclasses.replace(item, name=name)
        return item

    @t.override
    async def _delete(self, item_uid: int) -> None:
        self._get(item_uid)
        del self._items[item_uid]

    def _get(self, item_uid: int) -> ItemType:
        try:
            return self._items[item_uid]
        except KeyError:
            raise AuthItemNotFoundError.for_uid(self.REGISTRY, item_uid) from None

    def _check_name(self, name: str) -> None:
        if any(item.name == name for item in self._items.values()):
            raise AuthItemConflictError.for_name(self.REGISTRY, name)
