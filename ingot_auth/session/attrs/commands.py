"""The commands of the attributes of the sessions."""

__all__ = (
    "AuthCreateSessionAttrCommand",
    "AuthDeleteSessionAttrCommand",
    "AuthListSessionAttrsCommand",
    "AuthRenameSessionAttrCommand",
)

import argparse
import typing as t

from ingot_auth.registry import AuthAttrType
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

from .items import AuthSessionAttr, AuthSessionAttrSource
from .operations import (
    AuthCreateSessionAttr,
    AuthDeleteSessionAttr,
    AuthListSessionAttrs,
    AuthRenameSessionAttr,
)

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class BaseAuthSessionAttrsCommand[ParametersType, ResultType](
    BaseAuthRegistryCommand[AuthSessionAttr, ParametersType, ResultType]
):
    """
    A command of the attributes of the sessions: prints an attribute with its
    type and its source.
    """

    project: "AuthProject"

    @t.override
    def _format_item(self, item: AuthSessionAttr) -> str:
        return f"{super()._format_item(item)}\t{item.type}\t{item.source}"


class AuthCreateSessionAttrCommand(
    BaseAuthCreateItemCommand[AuthSessionAttr],
    BaseAuthSessionAttrsCommand[AuthSessionAttr, AuthSessionAttr],
):
    cli_description = "Creates an attribute of the sessions."

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        super()._cli_prepare_parser(parser)
        parser.add_argument(
            "--type",
            dest="session_attrs_type",
            type=AuthAttrType,
            choices=list(AuthAttrType),
            required=True,
        )
        parser.add_argument(
            "--source",
            dest="session_attrs_source",
            type=AuthSessionAttrSource,
            choices=list(AuthSessionAttrSource),
            required=True,
        )

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthSessionAttr:
        return AuthSessionAttr(
            id=namespace.registry_id,
            name=namespace.registry_name,
            type=namespace.session_attrs_type,
            source=namespace.session_attrs_source,
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthCreateSessionAttr]":
        return self.project.auth.session.attrs.op_create


class AuthListSessionAttrsCommand(
    BaseAuthListItemsCommand[AuthSessionAttr],
    BaseAuthSessionAttrsCommand[None, tuple[AuthSessionAttr, ...]],
):
    cli_description = "Prints the attributes of the sessions."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListSessionAttrs]":
        return self.project.auth.session.attrs.op_list


class AuthRenameSessionAttrCommand(
    BaseAuthRenameItemCommand[AuthSessionAttr],
    BaseAuthSessionAttrsCommand[AuthRenameItemParameters, AuthSessionAttr],
):
    cli_description = (
        "Gives an attribute of the sessions a new name; its type and source stay."
    )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRenameSessionAttr]":
        return self.project.auth.session.attrs.op_rename


class AuthDeleteSessionAttrCommand(
    BaseAuthDeleteItemCommand[AuthSessionAttr],
    BaseAuthSessionAttrsCommand[AuthDeleteItemParameters, None],
):
    cli_description = (
        "Deletes an attribute of the sessions; its id is never given again."
    )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthDeleteSessionAttr]":
        return self.project.auth.session.attrs.op_delete
