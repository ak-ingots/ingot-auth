"""The storage of a registry: the facade a backend implements, and one in memory."""

__all__ = ("AuthMemoryRegistryStorage", "BaseAuthRegistryStorage")

import abc
import dataclasses
import typing as t

from ingots.puer import Entity

from .errors import AuthItemConflictError, AuthItemNotFoundError
from .items import AuthItem

if t.TYPE_CHECKING:
    from ingots.puer import Project


class BaseAuthRegistryStorage[ItemType: AuthItem](Entity):
    """
    The storage of one registry, what a backend implements in the hooks. It
    guarantees the invariants, the operations decide the rest: ids and names
    are unique, and an id once taken is never taken again, even after its
    item is deleted.
    """

    # the name of the registry in the errors: tags, attrs
    REGISTRY: t.ClassVar[str]

    @t.final
    async def create(self, item: ItemType) -> None:
        """
        Stores a new item.

        :raises AuthItemConflictError: its id or its name is taken; the id
            of a deleted item stays taken.
        """
        await self._create(item)

    @t.final
    async def get_all(self) -> tuple[ItemType, ...]:
        """The items, by id."""
        return await self._get_all()

    @t.final
    async def rename(self, item_id: int, name: str) -> ItemType:
        """
        Gives an item a new name, returning the item renamed.

        :raises AuthItemNotFoundError: no item has the id.
        :raises AuthItemConflictError: the name is taken.
        """
        return await self._rename(item_id, name)

    @t.final
    async def delete(self, item_id: int) -> None:
        """
        Deletes an item; its id stays taken.

        :raises AuthItemNotFoundError: no item has the id.
        """
        await self._delete(item_id)

    @abc.abstractmethod
    async def _create(self, item: ItemType) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._create")

    @abc.abstractmethod
    async def _get_all(self) -> tuple[ItemType, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_all")

    @abc.abstractmethod
    async def _rename(self, item_id: int, name: str) -> ItemType:
        raise NotImplementedError(f"{type(self).__qualname__}._rename")

    @abc.abstractmethod
    async def _delete(self, item_id: int) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._delete")


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
