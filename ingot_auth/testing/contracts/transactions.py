"""The contract of the transactions of a storage, over all its storages."""

__all__ = ("AuthStorageTransactionsContract",)

from ingot_auth.storages import (
    AuthAttrType,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthTag,
    AuthTransactionError,
)

from .base import BaseAuthContract

BETA = AuthTag(id=1, name="beta")
DEVICE = AuthSessionAttr(
    id=1, name="device", type=AuthAttrType.STR, source=AuthSessionAttrSource.CLIENT
)


class AuthStorageTransactionsContract(BaseAuthContract):
    """
    The transactions of a storage: they span its storages, here a registry of
    the profiles and one of the sessions.
    """

    async def write(self) -> None:
        storage = self.project.auth.storage
        await storage.profiles.tags.create(BETA)
        await storage.sessions.attrs.create(DEVICE)

    async def assert_written(self, written: bool) -> None:
        storage = self.project.auth.storage
        self.assertEqual(
            (
                await storage.profiles.tags.get_all(),
                await storage.sessions.attrs.get_all(),
            ),
            ((BETA,), (DEVICE,)) if written else ((), ()),
        )

    async def test_a_commit_keeps_what_is_written(self) -> None:
        storage = self.project.auth.storage
        await storage.begin()
        await self.write()
        await storage.commit()
        await self.assert_written(True)

    async def test_a_rollback_undoes_what_is_written(self) -> None:
        storage = self.project.auth.storage
        await storage.begin()
        await self.write()
        await storage.rollback()
        await self.assert_written(False)

    async def test_a_rollback_keeps_what_was_there(self) -> None:
        storage = self.project.auth.storage
        await storage.profiles.tags.create(BETA)
        await storage.begin()
        await storage.profiles.tags.rename(1, "preview")
        await storage.rollback()
        self.assertEqual(await storage.profiles.tags.get_all(), (BETA,))

    async def test_a_block_is_committed(self) -> None:
        async with self.project.auth.storage.transaction():
            await self.write()
        await self.assert_written(True)

    async def test_a_block_raising_is_rolled_back(self) -> None:
        with self.assertRaises(LookupError):
            async with self.project.auth.storage.transaction():
                await self.write()
                raise LookupError
        await self.assert_written(False)

    async def test_a_block_inside_another_is_the_other(self) -> None:
        storage = self.project.auth.storage
        with self.assertRaises(LookupError):
            async with storage.transaction():
                async with storage.transaction():
                    await self.write()
                raise LookupError
        await self.assert_written(False)

    async def test_the_transaction_is_over_after_it_ends(self) -> None:
        storage = self.project.auth.storage
        async with storage.transaction():
            self.assertIsNotNone(storage.get_transaction())
        self.assertIsNone(storage.get_transaction())
        await storage.begin()
        await storage.rollback()
        self.assertIsNone(storage.get_transaction())

    async def test_a_transaction_is_begun_once(self) -> None:
        storage = self.project.auth.storage
        await storage.begin()
        with self.assertRaises(AuthTransactionError):
            await storage.begin()
        await storage.rollback()

    async def test_none_is_ended_unless_begun(self) -> None:
        storage = self.project.auth.storage
        for end in (storage.commit, storage.rollback):
            with self.assertRaises(AuthTransactionError):
                await end()
