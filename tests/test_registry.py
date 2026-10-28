import asyncio
import contextlib
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    ANONYMOUS_CALLER,
    ROOT_CALLER,
    OperationPermissionsError,
)
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.attrs import AuthAttr, AuthAttrType
from ingot_auth.registry import (
    AuthItemConflictError,
    AuthItemNotFoundError,
    BaseAuthRegistryStorage,
)
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.tags import AuthTag

BETA: t.Final = AuthTag(id=1, name="beta")
STAFF: t.Final = AuthTag(id=2, name="staff")


class TagsStorageTestCase(unittest.TestCase):
    """What every storage of the tags guarantees: a contract to be."""

    def create_storage(self) -> BaseAuthRegistryStorage[AuthTag]:
        self.project = AuthMemoryProject()  # the storage refers to it weakly
        return self.project.auth.storage.tags

    @t.override
    def setUp(self) -> None:
        self.storage = self.create_storage()
        asyncio.run(self.storage.create(STAFF))
        asyncio.run(self.storage.create(BETA))

    def test_the_items_come_by_id(self) -> None:
        self.assertEqual(asyncio.run(self.storage.get_all()), (BETA, STAFF))

    def test_an_id_or_a_name_is_taken_once(self) -> None:
        for item in (AuthTag(id=1, name="new"), AuthTag(id=3, name="beta")):
            with self.assertRaises(AuthItemConflictError) as error:
                asyncio.run(self.storage.create(item))
            self.assertEqual(error.exception.registry, "tags")

    def test_the_id_of_a_deleted_item_stays_taken(self) -> None:
        asyncio.run(self.storage.delete(1))
        self.assertEqual(asyncio.run(self.storage.get_all()), (STAFF,))
        with self.assertRaisesRegex(AuthItemConflictError, "the id 1 is not"):
            asyncio.run(self.storage.create(BETA))

    def test_an_item_is_renamed(self) -> None:
        renamed = AuthTag(id=1, name="preview")
        self.assertEqual(asyncio.run(self.storage.rename(1, "preview")), renamed)
        self.assertEqual(asyncio.run(self.storage.rename(1, "preview")), renamed)
        with self.assertRaisesRegex(AuthItemConflictError, "'staff' is not"):
            asyncio.run(self.storage.rename(1, "staff"))

    def test_an_unknown_id_is_not_found(self) -> None:
        with self.assertRaises(AuthItemNotFoundError) as error:
            asyncio.run(self.storage.rename(3, "new"))
        self.assertEqual(
            (str(error.exception), error.exception.key), ("tags: no item 3", 3)
        )
        with self.assertRaises(AuthItemNotFoundError):
            asyncio.run(self.storage.delete(3))


class RegistryOperationsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = AuthMemoryProject()
        operations = self.project.operations
        self.runner = operations.runner
        self.metadata = operations.create_metadata(ROOT_CALLER)
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))

    def test_the_tags_are_created_listed_renamed_deleted(self) -> None:
        tags = self.project.auth.tags

        async def run() -> tuple[AuthTag, ...]:
            await self.runner.run(tags.op_create, STAFF, self.metadata)
            await self.runner.run(tags.op_create, BETA, self.metadata)
            parameters = AuthRenameItemParameters(id=2, name="team")
            await self.runner.run(tags.op_rename, parameters, self.metadata)
            await self.runner.run(
                tags.op_delete, AuthDeleteItemParameters(id=1), self.metadata
            )
            return await self.runner.run(tags.op_list, None, self.metadata)

        self.assertEqual(asyncio.run(run()), (AuthTag(id=2, name="team"),))

    def test_an_attr_keeps_its_type_when_renamed(self) -> None:
        attrs = self.project.auth.attrs
        title = AuthAttr(id=1, name="title/en", type=AuthAttrType.STR)

        async def run() -> AuthAttr:
            await self.runner.run(attrs.op_create, title, self.metadata)
            parameters = AuthRenameItemParameters(id=1, name="title/be")
            return await self.runner.run(attrs.op_rename, parameters, self.metadata)

        self.assertEqual(asyncio.run(run()).type, AuthAttrType.STR)

    def test_wrong_ids_and_names_are_refused(self) -> None:
        tags = self.project.auth.tags
        for tag in (AuthTag(id=0, name="beta"), AuthTag(id=1, name="Beta")):
            with self.assertRaises(AuthItemConflictError):
                asyncio.run(self.runner.run(tags.op_create, tag, self.metadata))
        parameters = AuthRenameItemParameters(id=1, name="two words")
        with self.assertRaises(AuthItemConflictError):
            asyncio.run(self.runner.run(tags.op_rename, parameters, self.metadata))

    def test_a_caller_needs_the_permissions(self) -> None:
        metadata = self.project.operations.create_metadata(ANONYMOUS_CALLER)
        run = self.runner.run(self.project.auth.tags.op_list, None, metadata)
        with self.assertRaises(OperationPermissionsError):
            asyncio.run(run)


class RegistryCommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))
        self.enterContext(mock.patch("logging.config.dictConfig"))

    def run_project(self, *argv: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(
                AuthMemoryProject, ["--config", "IS_PRINT_CONFIGS=off", *argv]
            ).run()
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_the_commands_print_the_items(self) -> None:
        self.assertEqual(
            self.run_project("auth", "tags", "create", "--id", "1", "--name", "beta"),
            "1\tbeta\n",
        )
        self.assertEqual(
            self.run_project(
                "auth",
                "attrs",
                "create",
                "--id",
                "1",
                "--name",
                "phone",
                "--type",
                "str",
            ),
            "1\tphone\tstr\n",
        )

    def test_the_storage_in_memory_is_gone_with_the_command(self) -> None:
        for registry in ("tags", "attrs"):
            self.assertEqual(self.run_project("auth", registry, "list"), "")
            for argv in (
                ["rename", "--id", "1", "--name", "x"],
                ["delete", "--id", "1"],
            ):
                with self.assertLogs("ingots.puer.runner", "ERROR"):
                    code = CommandRunner(
                        AuthMemoryProject,
                        ["--config", "IS_PRINT_CONFIGS=off", "auth", registry, *argv],
                    ).run()
                self.assertEqual(code, 1)
