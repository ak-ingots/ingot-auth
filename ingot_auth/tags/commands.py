"""The commands of the tags."""

__all__ = (
    "AuthCreateTagCommand",
    "AuthDeleteTagCommand",
    "AuthListTagsCommand",
    "AuthRenameTagCommand",
)

import argparse
import typing as t

from ingot_auth.registry.commands import (
    BaseAuthCreateItemCommand,
    BaseAuthDeleteItemCommand,
    BaseAuthListItemsCommand,
    BaseAuthRenameItemCommand,
)

from .items import AuthTag
from .operations import AuthCreateTag, AuthDeleteTag, AuthListTags, AuthRenameTag

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class AuthCreateTagCommand(BaseAuthCreateItemCommand[AuthTag]):
    cli_description = "Creates a tag."
    project: "AuthProject"

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthTag:
        return AuthTag(id=namespace.registry_id, name=namespace.registry_name)

    @t.override
    def _get_create(self) -> "BoundFactory[AuthCreateTag]":
        return self.project.auth.tags.op_create


class AuthListTagsCommand(BaseAuthListItemsCommand[AuthTag]):
    cli_description = "Prints the tags."
    project: "AuthProject"

    @t.override
    def _get_list(self) -> "BoundFactory[AuthListTags]":
        return self.project.auth.tags.op_list


class AuthRenameTagCommand(BaseAuthRenameItemCommand[AuthTag]):
    cli_description = "Gives a tag a new name."
    project: "AuthProject"

    @t.override
    def _get_rename(self) -> "BoundFactory[AuthRenameTag]":
        return self.project.auth.tags.op_rename


class AuthDeleteTagCommand(BaseAuthDeleteItemCommand[AuthTag]):
    cli_description = "Deletes a tag; its id is never given again."
    project: "AuthProject"

    @t.override
    def _get_delete(self) -> "BoundFactory[AuthDeleteTag]":
        return self.project.auth.tags.op_delete
