import asyncio
import contextlib
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    OperationPermissionsError,
)
from ingots.puer import Slot
from ingots.puer.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import (
    AuthMemorySessionAttrsStorage,
    AuthMemorySessionPresetsStorage,
    AuthMemorySessionsStorage,
    AuthMemoryStorage,
)
from ingot_auth.metadata import (
    AuthMetadataUnit,
)
from ingot_auth.profiles.attrs import (
    AuthAttrsUnit,
)
from ingot_auth.profiles.tags import (
    AuthTagsUnit,
)
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.sessions.attrs import (
    AuthSessionAttrsUnit,
)
from ingot_auth.sessions.presets import (
    AuthSessionPresetsUnit,
)
from ingot_auth.sessions.presets.operations import AuthUnbindSessionAttrParameters
from ingot_auth.storages import (
    AuthAttr,
    AuthAttrType,
    AuthItemNotFoundError,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    AuthTag,
)

from tests import ANONYMOUS, QUIET, ROOT, masks

BETA: t.Final = AuthTag(uid=1, name="beta")
STAFF: t.Final = AuthTag(uid=2, name="staff")
IP: t.Final = AuthSessionAttr(
    uid=1, name="ip", type=AuthAttrType.STR, source=AuthSessionAttrSource.TRANSPORT
)
SIGN_IN: t.Final = AuthSessionPreset(uid=1, name="sign_in")


class SeededSessionAttrsStorage(AuthMemorySessionAttrsStorage):
    def __init__(self) -> None:
        super().__init__()
        self._items[IP.uid] = IP
        self._taken_ids.add(IP.uid)


class SeededSessionPresetsStorage(AuthMemorySessionPresetsStorage):
    def __init__(self) -> None:
        super().__init__()
        self._items[SIGN_IN.uid] = SIGN_IN
        self._taken_ids.add(SIGN_IN.uid)


class SeededSessionsStorage(AuthMemorySessionsStorage):
    attrs = Slot(SeededSessionAttrsStorage)
    presets = Slot(SeededSessionPresetsStorage)


class SeededStorage(AuthMemoryStorage):
    sessions = Slot(SeededSessionsStorage)


class SeededUnit(AuthMemoryUnit):
    storage = Slot(SeededStorage)


class SeededProject(AuthMemoryProject):
    auth = Slot(SeededUnit)


class RegistryOperationsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.project = AuthMemoryProject()
        operations = self.project.operations
        self.runner = operations.runner
        self.metadata = operations.create_metadata(ROOT)
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))

    def test_the_tags_are_created_listed_renamed_deleted(self) -> None:
        tags = self.project.auth.profiles.tags

        async def run() -> tuple[AuthTag, ...]:
            await self.runner.run(tags.op_create, STAFF, self.metadata)
            await self.runner.run(tags.op_create, BETA, self.metadata)
            parameters = AuthRenameItemParameters(uid=2, name="team")
            await self.runner.run(tags.op_rename, parameters, self.metadata)
            await self.runner.run(
                tags.op_delete, AuthDeleteItemParameters(uid=1), self.metadata
            )
            return await self.runner.run(tags.op_list, None, self.metadata)

        self.assertEqual(asyncio.run(run()), (AuthTag(uid=2, name="team"),))

    def test_an_attr_keeps_its_type_when_renamed(self) -> None:
        attrs = self.project.auth.profiles.attrs
        title = AuthAttr(uid=1, name="title/en", type=AuthAttrType.STR)

        async def run() -> AuthAttr:
            await self.runner.run(attrs.op_create, title, self.metadata)
            parameters = AuthRenameItemParameters(uid=1, name="title/be")
            return await self.runner.run(attrs.op_rename, parameters, self.metadata)

        self.assertEqual(asyncio.run(run()).type, AuthAttrType.STR)

    def test_a_session_attr_keeps_its_type_and_source_when_renamed(self) -> None:
        session_attrs = self.project.auth.sessions.attrs
        ip = AuthSessionAttr(
            uid=1,
            name="ip",
            type=AuthAttrType.STR,
            source=AuthSessionAttrSource.TRANSPORT,
        )

        async def run() -> AuthSessionAttr:
            await self.runner.run(session_attrs.op_create, ip, self.metadata)
            parameters = AuthRenameItemParameters(uid=1, name="peer/ip")
            return await self.runner.run(
                session_attrs.op_rename, parameters, self.metadata
            )

        renamed = asyncio.run(run())
        self.assertEqual(
            (renamed.type, renamed.source),
            (AuthAttrType.STR, AuthSessionAttrSource.TRANSPORT),
        )

    def test_an_attr_is_bound_to_a_preset_and_unbound(self) -> None:
        presets = self.project.auth.sessions.presets
        required = AuthSessionPresetBinding(preset_uid=1, attr_uid=1, required=True)

        async def run() -> tuple[AuthSessionPresetBinding, ...]:
            await self.runner.run(
                self.project.auth.sessions.attrs.op_create, IP, self.metadata
            )
            await self.runner.run(presets.op_create, SIGN_IN, self.metadata)
            optional = AuthSessionPresetBinding(
                preset_uid=1, attr_uid=1, required=False
            )
            bound = await self.runner.run(presets.op_bind, optional, self.metadata)
            self.assertEqual(bound, optional)
            await self.runner.run(presets.op_bind, required, self.metadata)
            bindings = await self.runner.run(
                presets.op_list_bindings, None, self.metadata
            )
            self.assertEqual(bindings, (required,))
            parameters = AuthUnbindSessionAttrParameters(preset_uid=1, attr_uid=1)
            await self.runner.run(presets.op_unbind, parameters, self.metadata)
            return await self.runner.run(presets.op_list_bindings, None, self.metadata)

        self.assertEqual(asyncio.run(run()), ())

    def test_only_an_attr_there_is_bound(self) -> None:
        presets = self.project.auth.sessions.presets
        binding = AuthSessionPresetBinding(preset_uid=1, attr_uid=1, required=True)

        async def run() -> None:
            await self.runner.run(presets.op_create, SIGN_IN, self.metadata)
            await self.runner.run(presets.op_bind, binding, self.metadata)

        with self.assertRaises(AuthItemNotFoundError) as error:
            asyncio.run(run())
        self.assertEqual(
            (error.exception.registry, error.exception.key), ("sessions.attrs", 1)
        )

    def test_a_deleted_attr_is_gone_from_the_presets(self) -> None:
        attrs = self.project.auth.sessions.attrs
        presets = self.project.auth.sessions.presets
        binding = AuthSessionPresetBinding(preset_uid=1, attr_uid=1, required=True)

        async def run() -> tuple[AuthSessionPresetBinding, ...]:
            await self.runner.run(attrs.op_create, IP, self.metadata)
            await self.runner.run(presets.op_create, SIGN_IN, self.metadata)
            await self.runner.run(presets.op_bind, binding, self.metadata)
            await self.runner.run(
                attrs.op_delete, AuthDeleteItemParameters(uid=1), self.metadata
            )
            return await self.runner.run(presets.op_list_bindings, None, self.metadata)

        self.assertEqual(asyncio.run(run()), ())

    def test_wrong_ids_and_names_are_refused(self) -> None:
        tags = self.project.auth.profiles.tags
        for tag in (AuthTag(uid=0, name="beta"), AuthTag(uid=1, name="Beta")):
            with self.assertRaises(AuthItemInvalidError):
                asyncio.run(self.runner.run(tags.op_create, tag, self.metadata))
        parameters = AuthRenameItemParameters(uid=1, name="two words")
        with self.assertRaises(AuthItemInvalidError):
            asyncio.run(self.runner.run(tags.op_rename, parameters, self.metadata))

    def test_a_caller_needs_the_permissions(self) -> None:
        metadata = self.project.operations.create_metadata(ANONYMOUS)
        run = self.runner.run(self.project.auth.profiles.tags.op_list, None, metadata)
        with self.assertRaises(OperationPermissionsError):
            asyncio.run(run)

    def test_every_operation_requires_its_permission(self) -> None:
        tags, attrs = self.project.auth.profiles.tags, self.project.auth.profiles.attrs
        session_attrs = self.project.auth.sessions.attrs
        presets = self.project.auth.sessions.presets
        for factory, flag in (
            (tags.op_create, AuthTagsUnit.Flags.CAN_CREATE),
            (tags.op_list, AuthTagsUnit.Flags.CAN_READ),
            (tags.op_rename, AuthTagsUnit.Flags.CAN_UPDATE),
            (tags.op_delete, AuthTagsUnit.Flags.CAN_DELETE),
            (attrs.op_create, AuthAttrsUnit.Flags.CAN_CREATE),
            (attrs.op_list, AuthAttrsUnit.Flags.CAN_READ),
            (attrs.op_rename, AuthAttrsUnit.Flags.CAN_UPDATE),
            (attrs.op_delete, AuthAttrsUnit.Flags.CAN_DELETE),
            (session_attrs.op_create, AuthSessionAttrsUnit.Flags.CAN_CREATE),
            (session_attrs.op_list, AuthSessionAttrsUnit.Flags.CAN_READ),
            (session_attrs.op_rename, AuthSessionAttrsUnit.Flags.CAN_RENAME),
            (session_attrs.op_delete, AuthSessionAttrsUnit.Flags.CAN_DELETE),
            (presets.op_create, AuthSessionPresetsUnit.Flags.CAN_CREATE),
            (presets.op_list, AuthSessionPresetsUnit.Flags.CAN_READ),
            (presets.op_rename, AuthSessionPresetsUnit.Flags.CAN_RENAME),
            (presets.op_delete, AuthSessionPresetsUnit.Flags.CAN_DELETE),
            (presets.op_bind, AuthSessionPresetsUnit.Flags.CAN_BIND),
            (presets.op_unbind, AuthSessionPresetsUnit.Flags.CAN_UNBIND),
            (presets.op_list_bindings, AuthSessionPresetsUnit.Flags.CAN_READ),
            (self.project.auth.metadata.op_get, AuthMetadataUnit.Flags.CAN_READ),
        ):
            self.assertEqual(factory().get_permissions(), masks(flag))


class RegistryCommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))

    def run_project(
        self, *argv: str, project_cls: type[AuthMemoryProject] = AuthMemoryProject
    ) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(project_cls, [*QUIET, *argv]).run()
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_the_commands_print_the_items(self) -> None:
        self.assertEqual(
            self.run_project(
                "auth", "profiles", "tags", "create", "--uid", "1", "--name", "beta"
            ),
            "1\tbeta\n",
        )
        self.assertEqual(
            self.run_project(
                "auth",
                "profiles",
                "attrs",
                "create",
                "--uid",
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
                "sessions",
                "attrs",
                "create",
                "--uid",
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

    def test_the_commands_of_the_presets_print_the_bindings(self) -> None:
        presets = ("auth", "sessions", "presets")
        self.assertEqual(
            self.run_project(*presets, "create", "--uid", "2", "--name", "sign_up"),
            "2\tsign_up\n",
        )
        for flags, requirement in (([], "optional"), (["--required"], "required")):
            self.assertEqual(
                self.run_project(
                    *presets,
                    "bind",
                    "--preset",
                    "1",
                    "--attr",
                    "1",
                    *flags,
                    project_cls=SeededProject,
                ),
                f"1\t1\t{requirement}\n",
            )
        self.assertEqual(self.run_project(*presets, "bindings"), "")
        with self.assertLogs("ingots.puer.runner", "ERROR"):
            code = CommandRunner(
                SeededProject,
                [
                    *QUIET,
                    *presets,
                    "unbind",
                    "--preset",
                    "1",
                    "--attr",
                    "1",
                ],
            ).run()
        self.assertEqual(code, 1)

    def test_the_storage_in_memory_is_gone_with_the_command(self) -> None:
        for unit, registry in (
            ("profiles", "tags"),
            ("profiles", "attrs"),
            ("sessions", "attrs"),
            ("sessions", "presets"),
        ):
            self.assertEqual(self.run_project("auth", unit, registry, "list"), "")
            for argv in (
                ["rename", "--uid", "1", "--name", "x"],
                ["delete", "--uid", "1"],
            ):
                with self.assertLogs("ingots.puer.runner", "ERROR"):
                    code = CommandRunner(
                        AuthMemoryProject,
                        [
                            *QUIET,
                            "auth",
                            unit,
                            registry,
                            *argv,
                        ],
                    ).run()
                self.assertEqual(code, 1)
