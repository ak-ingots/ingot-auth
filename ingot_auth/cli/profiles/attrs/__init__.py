"""The commands of the attributes of the profiles, ``auth profiles attrs``."""

__all__ = (
    "AuthAttrsCommandsUnit",
    "AuthCreateAttrCommand",
    "AuthDeleteAttrCommand",
    "AuthListAttrsCommand",
    "AuthRenameAttrCommand",
)

import argparse
import typing as t

from ingots.defaults.cli import CommandsUnit
from ingots.puer import Slot

from ingot_auth.cli.registry import (
    BaseAuthCreateItemCommand,
    BaseAuthDeleteItemCommand,
    BaseAuthListItemsCommand,
    BaseAuthRegistryCommand,
    BaseAuthRenameItemCommand,
)
from ingot_auth.profiles.attrs.operations import (
    AuthCreateAttrOperation,
    AuthDeleteAttrOperation,
    AuthListAttrsOperation,
    AuthRenameAttrOperation,
)
from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)
from ingot_auth.storages import AuthAttr, AuthAttrType

from .values import AuthProfileAttrValuesCommandsUnit

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class BaseAuthAttrsCommand[ParametersType, ResultType](
    BaseAuthRegistryCommand[AuthAttr, ParametersType, ResultType]
):
    """A command of the attributes: prints an attribute with its type."""

    project: "AuthProject"

    @t.override
    def _format_item(self, item: AuthAttr) -> str:
        return f"{super()._format_item(item)}\t{item.type}"


class AuthCreateAttrCommand(
    BaseAuthCreateItemCommand[AuthAttr], BaseAuthAttrsCommand[AuthAttr, AuthAttr]
):
    cli_description = "Creates an attribute."

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        super()._cli_prepare_parser(parser)
        parser.add_argument(
            "--type",
            dest="attrs_type",
            type=AuthAttrType,
            choices=list(AuthAttrType),
            required=True,
        )

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthAttr:
        return AuthAttr(
            uid=namespace.registry_uid,
            name=namespace.registry_name,
            type=namespace.attrs_type,
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthCreateAttrOperation]":
        return self.project.auth.profiles.attrs.op_create


class AuthListAttrsCommand(
    BaseAuthListItemsCommand[AuthAttr],
    BaseAuthAttrsCommand[None, tuple[AuthAttr, ...]],
):
    cli_description = "Prints the attributes."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListAttrsOperation]":
        return self.project.auth.profiles.attrs.op_list


class AuthRenameAttrCommand(
    BaseAuthRenameItemCommand[AuthAttr],
    BaseAuthAttrsCommand[AuthRenameItemParameters, AuthAttr],
):
    cli_description = "Gives an attribute a new name; its type stays."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRenameAttrOperation]":
        return self.project.auth.profiles.attrs.op_rename


class AuthDeleteAttrCommand(
    BaseAuthDeleteItemCommand[AuthAttr],
    BaseAuthAttrsCommand[AuthDeleteItemParameters, None],
):
    cli_description = "Deletes an attribute; its id is never given again."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthDeleteAttrOperation]":
        return self.project.auth.profiles.attrs.op_delete


class AuthAttrsCommandsUnit(CommandsUnit):
    cli_description = "The attributes of the profiles."
    create = Slot(AuthCreateAttrCommand)
    list = Slot(AuthListAttrsCommand)
    rename = Slot(AuthRenameAttrCommand)
    delete = Slot(AuthDeleteAttrCommand)
    values = Slot(AuthProfileAttrValuesCommandsUnit)
