"""The commands of the presets of the sessions."""

__all__ = (
    "AuthBindSessionAttrCommand",
    "AuthCreateSessionPresetCommand",
    "AuthDeleteSessionPresetCommand",
    "AuthListSessionPresetBindingsCommand",
    "AuthListSessionPresetsCommand",
    "AuthRenameSessionPresetCommand",
    "AuthUnbindSessionAttrCommand",
)

import argparse
import typing as t

from ingot_auth.registry.commands import (
    BaseAuthCreateItemCommand,
    BaseAuthDeleteItemCommand,
    BaseAuthListItemsCommand,
    BaseAuthRegistryCommand,
    BaseAuthRenameItemCommand,
)

from .items import AuthSessionPreset, AuthSessionPresetBinding
from .operations import (
    AuthBindSessionAttrOperation,
    AuthCreateSessionPresetOperation,
    AuthDeleteSessionPresetOperation,
    AuthListSessionPresetBindingsOperation,
    AuthListSessionPresetsOperation,
    AuthRenameSessionPresetOperation,
    AuthUnbindSessionAttrOperation,
    AuthUnbindSessionAttrParameters,
)

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class AuthCreateSessionPresetCommand(BaseAuthCreateItemCommand[AuthSessionPreset]):
    cli_description = "Creates a preset of the sessions."
    project: "AuthProject"

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthSessionPreset:
        return AuthSessionPreset(id=namespace.registry_id, name=namespace.registry_name)

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthCreateSessionPresetOperation]":
        return self.project.auth.sessions.presets.op_create


class AuthListSessionPresetsCommand(BaseAuthListItemsCommand[AuthSessionPreset]):
    cli_description = "Prints the presets of the sessions."
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListSessionPresetsOperation]":
        return self.project.auth.sessions.presets.op_list


class AuthRenameSessionPresetCommand(BaseAuthRenameItemCommand[AuthSessionPreset]):
    cli_description = "Gives a preset of the sessions a new name."
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRenameSessionPresetOperation]":
        return self.project.auth.sessions.presets.op_rename


class AuthDeleteSessionPresetCommand(BaseAuthDeleteItemCommand[AuthSessionPreset]):
    cli_description = (
        "Deletes a preset of the sessions with its bindings; its id is never "
        "given again."
    )
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthDeleteSessionPresetOperation]":
        return self.project.auth.sessions.presets.op_delete


class BaseAuthSessionPresetBindingsCommand[ParametersType, ResultType](
    BaseAuthRegistryCommand[AuthSessionPreset, ParametersType, ResultType]
):
    """
    A command of the bindings: prints a binding with the preset, the
    attribute and whether the preset requires it.
    """

    project: "AuthProject"

    @t.final
    def print_bindings(self, *bindings: AuthSessionPresetBinding) -> None:
        """Prints the bindings, one a line."""
        for binding in bindings:
            requirement = "required" if binding.required else "optional"
            print(f"{binding.preset_id}\t{binding.attr_id}\t{requirement}")


class AuthBindSessionAttrCommand(
    BaseAuthSessionPresetBindingsCommand[
        AuthSessionPresetBinding, AuthSessionPresetBinding
    ]
):
    cli_name = "bind"
    cli_description = (
        "Binds an attribute of the sessions to a preset, optional unless told "
        "--required; binding it again tells that anew."
    )
    cli_args: AuthSessionPresetBinding

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--preset", dest="presets_preset", type=int, required=True)
        parser.add_argument("--attr", dest="presets_attr", type=int, required=True)
        parser.add_argument("--required", dest="presets_required", action="store_true")

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthSessionPresetBinding:
        return AuthSessionPresetBinding(
            preset_id=namespace.presets_preset,
            attr_id=namespace.presets_attr,
            required=namespace.presets_required,
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthBindSessionAttrOperation]":
        return self.project.auth.sessions.presets.op_bind

    @t.override
    async def _run(self) -> None:
        self.print_bindings(await self.run_operation(self.cli_args))


class AuthUnbindSessionAttrCommand(
    BaseAuthSessionPresetBindingsCommand[AuthUnbindSessionAttrParameters, None]
):
    cli_name = "unbind"
    cli_description = "Unbinds an attribute of the sessions from a preset."
    cli_args: AuthUnbindSessionAttrParameters

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--preset", dest="presets_preset", type=int, required=True)
        parser.add_argument("--attr", dest="presets_attr", type=int, required=True)

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthUnbindSessionAttrParameters:
        return AuthUnbindSessionAttrParameters(
            preset_id=namespace.presets_preset, attr_id=namespace.presets_attr
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthUnbindSessionAttrOperation]":
        return self.project.auth.sessions.presets.op_unbind

    @t.override
    async def _run(self) -> None:
        await self.run_operation(self.cli_args)


class AuthListSessionPresetBindingsCommand(
    BaseAuthSessionPresetBindingsCommand[None, tuple[AuthSessionPresetBinding, ...]]
):
    cli_name = "bindings"
    cli_description = "Prints the bindings of the presets of the sessions."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListSessionPresetBindingsOperation]":
        return self.project.auth.sessions.presets.op_list_bindings

    @t.override
    async def _run(self) -> None:
        self.print_bindings(*await self.run_operation(None))
