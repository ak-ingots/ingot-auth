"""The contract of a storage: what a backend guarantees, whatever it runs on."""

__all__ = ("AuthAttrsStorageContract", "AuthTagsStorageContract")

import abc
import asyncio
import typing as t
import unittest

from ingot_auth.attrs import AuthAttr, AuthAttrType
from ingot_auth.registry import (
    AuthItem,
    AuthItemConflictError,
    AuthItemNotFoundError,
    AuthRegistryError,
    BaseAuthRegistryStorage,
)
from ingot_auth.tags import AuthTag

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = abc.ABC


class BaseAuthRegistryStorageContract[ItemType: AuthItem](TestCase):
    """
    A registry of a storage: a subclass tells which, a test case on what. Only
    what the storage promises is checked: the operations validate the items,
    so a storage is given acceptable ones.
    """

    REGISTRY: t.ClassVar[str]

    @abc.abstractmethod
    async def create_project(self) -> "AuthProject":
        """
        The project to run on, its storage empty. The test case cleans up what
        it needs to, with ``addAsyncCleanup()``.
        """
        raise NotImplementedError(f"{type(self).__qualname__}.create_project")

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = await self.create_project()
        self.storage = self._get_storage(self.project)

    async def test_it_is_empty_at_first(self) -> None:
        self.assertEqual(await self.storage.get_all(), ())

    async def test_an_item_is_given_as_created(self) -> None:
        item = self._create_item(1, "beta")
        await self.storage.create(item)
        self.assertEqual(await self.storage.get_all(), (item,))

    async def test_the_items_come_by_id(self) -> None:
        second, first = self._create_item(2, "b"), self._create_item(1, "c")
        await self.storage.create(second)
        await self.storage.create(first)
        self.assertEqual(await self.storage.get_all(), (first, second))

    async def test_an_id_is_taken_once(self) -> None:
        item = self._create_item(1, "beta")
        await self.storage.create(item)
        with self.assertRaises(AuthItemConflictError) as error:
            await self.storage.create(self._create_item(1, "other"))
        self._assert_error(error.exception, 1)
        self.assertEqual(await self.storage.get_all(), (item,))

    async def test_a_name_is_taken_once(self) -> None:
        item = self._create_item(1, "beta")
        await self.storage.create(item)
        with self.assertRaises(AuthItemConflictError) as error:
            await self.storage.create(self._create_item(2, "beta"))
        self._assert_error(error.exception, "beta")
        self.assertEqual(await self.storage.get_all(), (item,))

    async def test_the_id_of_a_deleted_item_stays_taken(self) -> None:
        await self.storage.create(self._create_item(1, "beta"))
        await self.storage.delete(1)
        self.assertEqual(await self.storage.get_all(), ())
        with self.assertRaises(AuthItemConflictError) as error:
            await self.storage.create(self._create_item(1, "other"))
        self._assert_error(error.exception, 1)

    async def test_the_name_of_a_deleted_item_is_free(self) -> None:
        await self.storage.create(self._create_item(1, "beta"))
        await self.storage.delete(1)
        item = self._create_item(2, "beta")
        await self.storage.create(item)
        self.assertEqual(await self.storage.get_all(), (item,))

    async def test_a_deleted_item_is_not_found(self) -> None:
        await self.storage.create(self._create_item(1, "beta"))
        await self.storage.delete(1)
        for call in (self.storage.delete(1), self.storage.rename(1, "other")):
            with self.assertRaises(AuthItemNotFoundError) as error:
                await call
            self._assert_error(error.exception, 1)

    async def test_an_unknown_id_is_not_found(self) -> None:
        for call in (self.storage.delete(1), self.storage.rename(1, "other")):
            with self.assertRaises(AuthItemNotFoundError) as error:
                await call
            self._assert_error(error.exception, 1)

    async def test_a_rename_gives_the_item_renamed(self) -> None:
        await self.storage.create(self._create_item(1, "beta"))
        renamed = self._create_item(1, "preview")
        self.assertEqual(await self.storage.rename(1, "preview"), renamed)
        self.assertEqual(await self.storage.get_all(), (renamed,))

    async def test_a_rename_frees_the_old_name(self) -> None:
        await self.storage.create(self._create_item(1, "beta"))
        await self.storage.rename(1, "preview")
        await self.storage.create(self._create_item(2, "beta"))
        self.assertEqual(len(await self.storage.get_all()), 2)

    async def test_a_rename_to_a_taken_name_changes_nothing(self) -> None:
        first, second = self._create_item(1, "a"), self._create_item(2, "b")
        await self.storage.create(first)
        await self.storage.create(second)
        with self.assertRaises(AuthItemConflictError) as error:
            await self.storage.rename(1, "b")
        self._assert_error(error.exception, "b")
        self.assertEqual(await self.storage.get_all(), (first, second))

    async def test_a_rename_to_its_own_name_changes_nothing(self) -> None:
        item = self._create_item(1, "beta")
        await self.storage.create(item)
        self.assertEqual(await self.storage.rename(1, "beta"), item)

    async def test_of_concurrent_creates_of_an_id_one_wins(self) -> None:
        await self._assert_one_wins(
            self._create_item(1, "a"), self._create_item(1, "b")
        )

    async def test_of_concurrent_creates_of_a_name_one_wins(self) -> None:
        await self._assert_one_wins(
            self._create_item(1, "a"), self._create_item(2, "a")
        )

    @abc.abstractmethod
    def _get_storage(self, project: "AuthProject") -> BaseAuthRegistryStorage[ItemType]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_storage")

    @abc.abstractmethod
    def _create_item(self, item_id: int, name: str) -> ItemType:
        raise NotImplementedError(f"{type(self).__qualname__}._create_item")

    def _assert_error(self, error: AuthRegistryError, key: int | str) -> None:
        self.assertEqual((error.registry, error.key), (self.REGISTRY, key))

    async def _assert_one_wins(self, *items: ItemType) -> None:
        results = await asyncio.gather(
            *map(self.storage.create, items), return_exceptions=True
        )
        conflicts = [r for r in results if isinstance(r, AuthItemConflictError)]
        self.assertEqual(len(conflicts), len(items) - 1, results)
        self.assertEqual(len(await self.storage.get_all()), 1)


class AuthTagsStorageContract(BaseAuthRegistryStorageContract[AuthTag]):
    """The tags of a storage."""

    REGISTRY: t.ClassVar[str] = "tags"

    @t.override
    def _get_storage(self, project: "AuthProject") -> BaseAuthRegistryStorage[AuthTag]:
        return project.auth.storage.tags

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthTag:
        return AuthTag(id=item_id, name=name)


class AuthAttrsStorageContract(BaseAuthRegistryStorageContract[AuthAttr]):
    """The attributes of a storage: each keeps its type."""

    REGISTRY: t.ClassVar[str] = "attrs"

    async def test_every_type_is_given_as_created(self) -> None:
        attrs = tuple(
            AuthAttr(id=item_id, name=item_type.value, type=item_type)
            for item_id, item_type in enumerate(AuthAttrType, start=1)
        )
        for attr in attrs:
            await self.storage.create(attr)
        self.assertEqual(await self.storage.get_all(), attrs)

    async def test_a_rename_keeps_the_type(self) -> None:
        attr = AuthAttr(id=1, name="phone", type=AuthAttrType.BOOL)
        await self.storage.create(attr)
        renamed = await self.storage.rename(1, "mobile")
        self.assertEqual(renamed.type, AuthAttrType.BOOL)
        self.assertEqual(await self.storage.get_all(), (renamed,))

    @t.override
    def _get_storage(self, project: "AuthProject") -> BaseAuthRegistryStorage[AuthAttr]:
        return project.auth.storage.attrs

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthAttr:
        return AuthAttr(id=item_id, name=name, type=AuthAttrType.STR)
