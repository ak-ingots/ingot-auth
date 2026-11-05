"""The contract of a storage: what a backend guarantees, whatever it runs on."""

__all__ = (
    "AuthAttrsStorageContract",
    "AuthSessionAttrsStorageContract",
    "AuthSessionPresetsStorageContract",
    "AuthTagsStorageContract",
)

import abc
import asyncio
import dataclasses
import typing as t

from ingot_auth.profiles.attrs import AuthAttr
from ingot_auth.profiles.tags import AuthTag
from ingot_auth.registry import (
    AuthAttrType,
    AuthItem,
    AuthItemConflictError,
    AuthItemNotFoundError,
    AuthRegistryError,
    BaseAuthRegistryStorage,
)
from ingot_auth.sessions.attrs import AuthSessionAttr, AuthSessionAttrSource
from ingot_auth.sessions.presets import (
    AuthSessionPreset,
    AuthSessionPresetBinding,
    BaseAuthSessionPresetsStorage,
)

from .base import BaseAuthContract

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthRegistryStorageContract[ItemType: AuthItem](BaseAuthContract):
    """
    A registry of a storage: a subclass tells which, a test case on what. Only
    what the storage promises is checked: the operations validate the items,
    so a storage is given acceptable ones.
    """

    REGISTRY: t.ClassVar[str]

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
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

    REGISTRY: t.ClassVar[str] = "profiles.tags"

    @t.override
    def _get_storage(self, project: "AuthProject") -> BaseAuthRegistryStorage[AuthTag]:
        return project.auth.storage.profiles.tags

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthTag:
        return AuthTag(id=item_id, name=name)


class AuthAttrsStorageContract(BaseAuthRegistryStorageContract[AuthAttr]):
    """The attributes of a storage: each keeps its type."""

    REGISTRY: t.ClassVar[str] = "profiles.attrs"

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
        return project.auth.storage.profiles.attrs

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthAttr:
        return AuthAttr(id=item_id, name=name, type=AuthAttrType.STR)


class AuthSessionAttrsStorageContract(BaseAuthRegistryStorageContract[AuthSessionAttr]):
    """The attributes of the sessions of a storage: each keeps its type and source."""

    REGISTRY: t.ClassVar[str] = "sessions.attrs"

    async def test_every_type_and_source_is_given_as_created(self) -> None:
        pairs = [
            (item_type, source)
            for item_type in AuthAttrType
            for source in AuthSessionAttrSource
        ]
        session_attrs = tuple(
            AuthSessionAttr(
                id=item_id,
                name=f"{item_type.value}_{source.value}",
                type=item_type,
                source=source,
            )
            for item_id, (item_type, source) in enumerate(pairs, start=1)
        )
        for session_attr in session_attrs:
            await self.storage.create(session_attr)
        self.assertEqual(await self.storage.get_all(), session_attrs)

    async def test_a_rename_keeps_the_type_and_the_source(self) -> None:
        session_attr = AuthSessionAttr(
            id=1,
            name="ip",
            type=AuthAttrType.STR,
            source=AuthSessionAttrSource.TRANSPORT,
        )
        await self.storage.create(session_attr)
        renamed = await self.storage.rename(1, "peer/ip")
        self.assertEqual(
            (renamed.type, renamed.source),
            (AuthAttrType.STR, AuthSessionAttrSource.TRANSPORT),
        )
        self.assertEqual(await self.storage.get_all(), (renamed,))

    @t.override
    def _get_storage(
        self, project: "AuthProject"
    ) -> BaseAuthRegistryStorage[AuthSessionAttr]:
        return project.auth.storage.sessions.attrs

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthSessionAttr:
        return AuthSessionAttr(
            id=item_id,
            name=name,
            type=AuthAttrType.STR,
            source=AuthSessionAttrSource.CLIENT,
        )


class AuthSessionPresetsStorageContract(
    BaseAuthRegistryStorageContract[AuthSessionPreset]
):
    """
    The presets of the sessions of a storage, with their bindings: any
    attribute id is bound, the operations look whether it is there.
    """

    REGISTRY: t.ClassVar[str] = "sessions.presets"

    storage: BaseAuthSessionPresetsStorage

    async def test_there_are_no_bindings_at_first(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        self.assertEqual(await self.storage.get_bindings(), ())

    async def test_the_bindings_come_by_the_preset_then_the_attr(self) -> None:
        for item_id, name in ((2, "sign_up"), (1, "sign_in")):
            await self.storage.create(self._create_item(item_id, name))
        bindings = (
            AuthSessionPresetBinding(preset_id=1, attr_id=3, required=True),
            AuthSessionPresetBinding(preset_id=1, attr_id=7, required=False),
            AuthSessionPresetBinding(preset_id=2, attr_id=3, required=False),
        )
        for binding in reversed(bindings):
            await self.storage.bind(binding)
        self.assertEqual(await self.storage.get_bindings(), bindings)

    async def test_binding_again_tells_the_requirement_anew(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        for required in (False, True):
            binding = AuthSessionPresetBinding(
                preset_id=1, attr_id=3, required=required
            )
            await self.storage.bind(binding)
        self.assertEqual(await self.storage.get_bindings(), (binding,))

    async def test_an_unbound_attr_is_gone(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        kept = AuthSessionPresetBinding(preset_id=1, attr_id=7, required=False)
        await self.storage.bind(kept)
        await self.storage.bind(
            AuthSessionPresetBinding(preset_id=1, attr_id=3, required=True)
        )
        await self.storage.unbind(1, 3)
        self.assertEqual(await self.storage.get_bindings(), (kept,))

    async def test_an_attr_not_bound_is_not_found(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        with self.assertRaises(AuthItemNotFoundError) as error:
            await self.storage.unbind(1, 3)
        self._assert_error(error.exception, "1:3")

    async def test_a_preset_not_there_is_not_found(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        await self.storage.delete(1)
        binding = AuthSessionPresetBinding(preset_id=1, attr_id=3, required=True)
        for preset_id in (1, 2):
            for call in (
                self.storage.bind(dataclasses.replace(binding, preset_id=preset_id)),
                self.storage.unbind(preset_id, 3),
            ):
                with self.assertRaises(AuthItemNotFoundError) as error:
                    await call
                self._assert_error(error.exception, preset_id)

    async def test_the_bindings_go_with_their_preset(self) -> None:
        for item_id, name in ((1, "sign_in"), (2, "sign_up")):
            await self.storage.create(self._create_item(item_id, name))
        kept = AuthSessionPresetBinding(preset_id=2, attr_id=3, required=True)
        await self.storage.bind(
            AuthSessionPresetBinding(preset_id=1, attr_id=3, required=True)
        )
        await self.storage.bind(kept)
        await self.storage.delete(1)
        self.assertEqual(await self.storage.get_bindings(), (kept,))

    async def test_a_rename_keeps_the_bindings(self) -> None:
        await self.storage.create(self._create_item(1, "sign_in"))
        binding = AuthSessionPresetBinding(preset_id=1, attr_id=3, required=True)
        await self.storage.bind(binding)
        await self.storage.rename(1, "sign_in/apple")
        self.assertEqual(await self.storage.get_bindings(), (binding,))

    @t.override
    def _get_storage(self, project: "AuthProject") -> BaseAuthSessionPresetsStorage:
        return project.auth.storage.sessions.presets

    @t.override
    def _create_item(self, item_id: int, name: str) -> AuthSessionPreset:
        return AuthSessionPreset(id=item_id, name=name)
