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
    Permissions,
)
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.attrs import AuthAttr, AuthAttrsPermissions, AuthAttrType
from ingot_auth.metadata import AuthMetadataPermissions
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.session_attrs import (
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionAttrsPermissions,
)
from ingot_auth.tags import AuthTag, AuthTagsPermissions

BETA: t.Final = AuthTag(id=1, name="beta")
STAFF: t.Final = AuthTag(id=2, name="staff")


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

    def test_a_session_attr_keeps_its_type_and_source_when_renamed(self) -> None:
        session_attrs = self.project.auth.session_attrs
        ip = AuthSessionAttr(
            id=1,
            name="ip",
            type=AuthAttrType.STR,
            source=AuthSessionAttrSource.TRANSPORT,
        )

        async def run() -> AuthSessionAttr:
            await self.runner.run(session_attrs.op_create, ip, self.metadata)
            parameters = AuthRenameItemParameters(id=1, name="peer/ip")
            return await self.runner.run(
                session_attrs.op_rename, parameters, self.metadata
            )

        renamed = asyncio.run(run())
        self.assertEqual(
            (renamed.type, renamed.source),
            (AuthAttrType.STR, AuthSessionAttrSource.TRANSPORT),
        )

    def test_wrong_ids_and_names_are_refused(self) -> None:
        tags = self.project.auth.tags
        for tag in (AuthTag(id=0, name="beta"), AuthTag(id=1, name="Beta")):
            with self.assertRaises(AuthItemInvalidError):
                asyncio.run(self.runner.run(tags.op_create, tag, self.metadata))
        parameters = AuthRenameItemParameters(id=1, name="two words")
        with self.assertRaises(AuthItemInvalidError):
            asyncio.run(self.runner.run(tags.op_rename, parameters, self.metadata))

    def test_a_caller_needs_the_permissions(self) -> None:
        metadata = self.project.operations.create_metadata(ANONYMOUS_CALLER)
        run = self.runner.run(self.project.auth.tags.op_list, None, metadata)
        with self.assertRaises(OperationPermissionsError):
            asyncio.run(run)

    def test_every_operation_requires_its_permission(self) -> None:
        tags, attrs = self.project.auth.tags, self.project.auth.attrs
        session_attrs = self.project.auth.session_attrs
        for factory, flag in (
            (tags.op_create, AuthTagsPermissions.CAN_CREATE),
            (tags.op_list, AuthTagsPermissions.CAN_READ),
            (tags.op_rename, AuthTagsPermissions.CAN_UPDATE),
            (tags.op_delete, AuthTagsPermissions.CAN_DELETE),
            (attrs.op_create, AuthAttrsPermissions.CAN_CREATE),
            (attrs.op_list, AuthAttrsPermissions.CAN_READ),
            (attrs.op_rename, AuthAttrsPermissions.CAN_UPDATE),
            (attrs.op_delete, AuthAttrsPermissions.CAN_DELETE),
            (session_attrs.op_create, AuthSessionAttrsPermissions.CAN_CREATE),
            (session_attrs.op_list, AuthSessionAttrsPermissions.CAN_READ),
            (session_attrs.op_rename, AuthSessionAttrsPermissions.CAN_RENAME),
            (session_attrs.op_delete, AuthSessionAttrsPermissions.CAN_DELETE),
            (self.project.auth.metadata.op_get, AuthMetadataPermissions.CAN_READ),
        ):
            self.assertEqual(factory.cls.PERMISSIONS, Permissions(flag))


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
        self.assertEqual(
            self.run_project(
                "auth",
                "session-attrs",
                "create",
                "--id",
                "1",
                "--name",
                "ip",
                "--type",
                "str",
                "--source",
                "transport",
            ),
            "1\tip\tstr\ttransport\n",
        )

    def test_the_storage_in_memory_is_gone_with_the_command(self) -> None:
        for registry in ("tags", "attrs", "session-attrs"):
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
