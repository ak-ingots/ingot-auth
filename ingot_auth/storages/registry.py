"""The storage of a registry: the facade a backend implements."""

__all__ = ("BaseAuthRegistryStorage",)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthItem


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
