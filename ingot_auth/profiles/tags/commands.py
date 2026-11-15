"""The commands of the tags."""

__all__ = (
    "AuthCreateTagCommand",
    "AuthDeleteTagCommand",
    "AuthListTagsCommand",
    "AuthRenameTagCommand",
    "AuthSetProfileTagsCommand",
)

import argparse
import typing as t

from ingot_auth.profiles.commands import BaseAuthProfileValuesCommand
from ingot_auth.profiles.items import AuthSetProfileTagsParameters
from ingot_auth.registry.commands import (
    BaseAuthCreateItemCommand,
    BaseAuthDeleteItemCommand,
    BaseAuthListItemsCommand,
    BaseAuthRenameItemCommand,
)
from ingot_auth.storages import AuthTag

from .operations import (
    AuthCreateTagOperation,
    AuthDeleteTagOperation,
    AuthListTagsOperation,
    AuthRenameTagOperation,
)

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.profiles.operations import AuthSetProfileTagsOperation
    from ingot_auth.project import AuthProject


class AuthCreateTagCommand(BaseAuthCreateItemCommand[AuthTag]):
    cli_description = "Creates a tag."
    project: "AuthProject"

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthTag:
        return AuthTag(uid=namespace.registry_uid, name=namespace.registry_name)

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthCreateTagOperation]":
        return self.project.auth.profiles.tags.op_create


class AuthListTagsCommand(BaseAuthListItemsCommand[AuthTag]):
    cli_description = "Prints the tags."
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListTagsOperation]":
        return self.project.auth.profiles.tags.op_list


class AuthRenameTagCommand(BaseAuthRenameItemCommand[AuthTag]):
    cli_description = "Gives a tag a new name."
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRenameTagOperation]":
        return self.project.auth.profiles.tags.op_rename


class AuthDeleteTagCommand(BaseAuthDeleteItemCommand[AuthTag]):
    cli_description = "Deletes a tag; its id is never given again."
    project: "AuthProject"

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthDeleteTagOperation]":
        return self.project.auth.profiles.tags.op_delete


class AuthSetProfileTagsCommand(
    BaseAuthProfileValuesCommand[AuthSetProfileTagsParameters]
):
    """Sets the tags of a profile by their ids, then prints its values."""

    cli_name = "set"
    cli_description = (
        "Sets the tags of a profile, all of them, by their ids: none takes them "
        "all off."
    )
    cli_args: AuthSetProfileTagsParameters

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("profiles_uid", metavar="uid")
        parser.add_argument("profiles_tags", metavar="tag", type=int, nargs="*")

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthSetProfileTagsParameters:
        return AuthSetProfileTagsParameters(
            uid=namespace.profiles_uid, tag_uids=frozenset(namespace.profiles_tags)
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthSetProfileTagsOperation]":
        return self.project.auth.profiles.op_set_tags

    @t.override
    async def _run(self) -> None:
        self.print_values(await self.run_operation(self.cli_args))
