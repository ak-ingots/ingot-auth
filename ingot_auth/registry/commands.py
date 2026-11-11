"""The commands of a registry: its operations run by the administrator."""

__all__ = (
    "AuthItemIdCliArgs",
    "AuthRenameItemCliArgs",
    "BaseAuthCreateItemCommand",
    "BaseAuthDeleteItemCommand",
    "BaseAuthListItemsCommand",
    "BaseAuthRegistryCommand",
    "BaseAuthRenameItemCommand",
)

import argparse
import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperationCommand

from ingot_auth.storages import AuthItem

from .operations import AuthDeleteItemParameters, AuthRenameItemParameters


@dataclass(frozen=True, slots=True)
class AuthItemIdCliArgs:
    id: int


@dataclass(frozen=True, slots=True)
class AuthRenameItemCliArgs:
    id: int
    name: str


class BaseAuthRegistryCommand[ItemType: AuthItem, ParametersType, ResultType](
    BaseOperationCommand[ParametersType, ResultType]
):
    """
    A command of a registry: runs its operation, which a subclass gives in
    :meth:`_get_operation`, as the root, and prints the items, one a line,
    as :meth:`_format_item` gives them.
    """

    @t.final
    def print_items(self, *items: ItemType) -> None:
        """Prints the items, one a line."""
        for item in items:
            print(self._format_item(item))

    def _format_item(self, item: ItemType) -> str:
        """An item on its line: its id and its name."""
        return f"{item.id}\t{item.name}"


class BaseAuthCreateItemCommand[ItemType: AuthItem](
    BaseAuthRegistryCommand[ItemType, ItemType, ItemType]
):
    """
    Creates an item: a subclass adds the options of its items and builds
    them from the namespace as its CLI arguments.
    """

    cli_name = "create"
    cli_description = "Creates an item."
    cli_args: ItemType

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", dest="registry_id", type=int, required=True)
        parser.add_argument("--name", dest="registry_name", required=True)

    @t.override
    async def _run(self) -> None:
        self.print_items(await self.run_operation(self.cli_args))


class BaseAuthListItemsCommand[ItemType: AuthItem](
    BaseAuthRegistryCommand[ItemType, None, tuple[ItemType, ...]]
):
    """Prints the items, by id."""

    cli_name = "list"
    cli_description = "Prints the items."

    @t.override
    async def _run(self) -> None:
        self.print_items(*await self.run_operation(None))


class BaseAuthRenameItemCommand[ItemType: AuthItem](
    BaseAuthRegistryCommand[ItemType, AuthRenameItemParameters, ItemType]
):
    """Gives an item a new name."""

    cli_name = "rename"
    cli_description = "Gives an item a new name."
    cli_args: AuthRenameItemCliArgs

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", dest="registry_id", type=int, required=True)
        parser.add_argument("--name", dest="registry_name", required=True)

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthRenameItemCliArgs:
        return AuthRenameItemCliArgs(namespace.registry_id, namespace.registry_name)

    @t.override
    async def _run(self) -> None:
        parameters = AuthRenameItemParameters(
            id=self.cli_args.id, name=self.cli_args.name
        )
        self.print_items(await self.run_operation(parameters))


class BaseAuthDeleteItemCommand[ItemType: AuthItem](
    BaseAuthRegistryCommand[ItemType, AuthDeleteItemParameters, None]
):
    """Deletes an item; its id is never given again."""

    cli_name = "delete"
    cli_description = "Deletes an item; its id is never given again."
    cli_args: AuthItemIdCliArgs

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--id", dest="registry_id", type=int, required=True)

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthItemIdCliArgs:
        return AuthItemIdCliArgs(namespace.registry_id)

    @t.override
    async def _run(self) -> None:
        parameters = AuthDeleteItemParameters(id=self.cli_args.id)
        await self.run_operation(parameters)
