"""The commands of the attributes."""

__all__ = (
    "AuthCreateAttrCommand",
    "AuthDeleteAttrCommand",
    "AuthListAttrsCommand",
    "AuthRenameAttrCommand",
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

from ingot_auth.registry.operations import (
    AuthDeleteItemParameters,
    AuthRenameItemParameters,
)

from .items import AuthAttr, AuthAttrType
from .operations import AuthCreateAttr, AuthDeleteAttr, AuthListAttrs, AuthRenameAttr

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
            id=namespace.registry_id,
            name=namespace.registry_name,
            type=namespace.attrs_type,
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthCreateAttr]":
        return self.project.auth.attrs.op_create


class AuthListAttrsCommand(
    BaseAuthListItemsCommand[AuthAttr],
    BaseAuthAttrsCommand[None, tuple[AuthAttr, ...]],
):
    cli_description = "Prints the attributes."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListAttrs]":
        return self.project.auth.attrs.op_list


class AuthRenameAttrCommand(
    BaseAuthRenameItemCommand[AuthAttr],
    BaseAuthAttrsCommand[AuthRenameItemParameters, AuthAttr],
):
    cli_description = "Gives an attribute a new name; its type stays."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRenameAttr]":
        return self.project.auth.attrs.op_rename


class AuthDeleteAttrCommand(
    BaseAuthDeleteItemCommand[AuthAttr],
    BaseAuthAttrsCommand[AuthDeleteItemParameters, None],
):
    cli_description = "Deletes an attribute; its id is never given again."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthDeleteAttr]":
        return self.project.auth.attrs.op_delete
