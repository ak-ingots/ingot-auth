"""The commands of the memberships."""

__all__ = (
    "AuthAddMemberCommand",
    "AuthListMemberGroupsCommand",
    "AuthListMembersCommand",
    "AuthRemoveMemberCommand",
)

import argparse
import typing as t

from ingot_auth.access.commands import BaseAuthAccessCommand

from .items import AuthMembership
from .operations import (
    AuthAddMember,
    AuthListMemberGroups,
    AuthListMembers,
    AuthRemoveMember,
)

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory


class BaseAuthMembershipCommand(BaseAuthAccessCommand[AuthMembership, None]):
    """A command on a membership: the group and the uid, as arguments."""

    cli_args: AuthMembership

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("members_group", metavar="group")
        parser.add_argument("members_uid", metavar="uid")

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> AuthMembership:
        return AuthMembership(group=namespace.members_group, uid=namespace.members_uid)

    @t.override
    async def _run(self) -> None:
        await self.run_operation(self.cli_args)


class AuthAddMemberCommand(BaseAuthMembershipCommand):
    cli_name = "add"
    cli_description = "Adds a user to a group; a member already stays one."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthAddMember]":
        return self.project.auth.access.members.op_add


class AuthRemoveMemberCommand(BaseAuthMembershipCommand):
    cli_name = "remove"
    cli_description = "Removes a user from a group."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRemoveMember]":
        return self.project.auth.access.members.op_remove


class AuthListMembersCommand(BaseAuthAccessCommand[str, tuple[str, ...]]):
    cli_name = "list"
    cli_description = "Prints the uids of the members of a group, one a line."
    cli_args: str

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("members_group", metavar="group")

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> str:
        return t.cast(str, namespace.members_group)

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListMembers]":
        return self.project.auth.access.members.op_list

    @t.override
    async def _run(self) -> None:
        for uid in await self.run_operation(self.cli_args):
            print(uid)


class AuthListMemberGroupsCommand(BaseAuthAccessCommand[str, tuple[str, ...]]):
    cli_name = "list-groups"
    cli_description = "Prints the groups a user is added to, one a line."
    cli_args: str

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("members_uid", metavar="uid")

    @t.override
    @classmethod
    def _cli_build_args(cls, namespace: argparse.Namespace) -> str:
        return t.cast(str, namespace.members_uid)

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListMemberGroups]":
        return self.project.auth.access.members.op_list_groups

    @t.override
    async def _run(self) -> None:
        for group in await self.run_operation(self.cli_args):
            print(group)
