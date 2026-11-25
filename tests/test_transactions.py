"""The events held by a transaction of the storage: the facade of the core."""

import dataclasses
import typing as t
import unittest

from ingots.defaults.operations import (
    BaseOperation,
    Caller,
    OperationMetadata,
    Permissions,
)
from ingots.puer import Factories, Slot, Unit

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import AuthMemoryStorage


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Written:
    uid: str


class SeeOperation(BaseOperation[Written, None]):
    project: "ShopProject"

    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()

    @t.override
    async def _run(self, parameters: Written, metadata: OperationMetadata) -> None:
        self.project.shop.seen.append(parameters.uid)


class ShopUnit(Unit):
    ev_written = Factories[BaseOperation[Written, None]](SeeOperation)

    def __init__(self) -> None:
        super().__init__()
        self.seen: list[str] = []


class FailingStorage(AuthMemoryStorage):
    @t.override
    async def _commit(self, transaction: object) -> None:
        raise ConnectionError("the commit is lost")


class FailingAuth(AuthMemoryUnit):
    storage = Slot(FailingStorage)


class ShopProject(AuthMemoryProject):
    shop = Slot(ShopUnit)


class FailingProject(ShopProject):
    auth = Slot(FailingAuth)


class TransactionEventsTestCase(unittest.IsolatedAsyncioTestCase):
    project: ShopProject

    @t.override
    async def asyncSetUp(self) -> None:
        self.project = ShopProject()
        self.metadata = self.project.operations.create_metadata(Caller(uid="u"))

    def publish(self, uid: str) -> None:
        shop = self.project.shop
        self.project.events.publish(shop.ev_written, Written(uid=uid), self.metadata)

    async def test_a_commit_sends_the_events_of_its_block(self) -> None:
        async with self.project.auth.storage.transaction():
            self.publish("a")
            await self.project.events.join()
            self.assertEqual(self.project.shop.seen, [])
        await self.project.events.join()
        self.assertEqual(self.project.shop.seen, ["a"])

    async def test_a_rollback_drops_them(self) -> None:
        with self.assertRaises(LookupError):
            async with self.project.auth.storage.transaction():
                self.publish("a")
                raise LookupError
        await self.project.events.join()
        self.assertEqual(self.project.shop.seen, [])

    async def test_a_failed_commit_drops_them(self) -> None:
        self.project = FailingProject()
        with self.assertRaises(ConnectionError):
            async with self.project.auth.storage.transaction():
                self.publish("a")
        await self.project.events.join()
        self.assertEqual(self.project.shop.seen, [])

    async def test_a_block_inside_another_sends_with_the_other(self) -> None:
        storage = self.project.auth.storage
        async with storage.transaction():
            async with storage.transaction():
                self.publish("a")
            await self.project.events.join()
            self.assertEqual(self.project.shop.seen, [])
        await self.project.events.join()
        self.assertEqual(self.project.shop.seen, ["a"])
