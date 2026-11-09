"""The commands of the groups."""

__all__ = ("AuthListGroupsCommand",)

import typing as t

from ingot_auth.access.commands import BaseAuthAccessCommand

from .items import AuthGroupInfo
from .operations import AuthListGroups

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory


class AuthListGroupsCommand(BaseAuthAccessCommand[None, tuple[AuthGroupInfo, ...]]):
    """
    Prints the groups, one a line: the name, then what it grants, a mask a
    domain, sorted by the domain: ``auth.access.members=3``.
    """

    cli_name = "list"
    cli_description = "Prints the groups and what each grants."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListGroups]":
        return self.project.auth.access.groups.op_list

    @t.override
    async def _run(self) -> None:
        for group in await self.run_operation(None):
            permissions = sorted(group.permissions.items())
            masks = (f"{domain}={mask}" for domain, mask in permissions)
            print("\t".join((group.name, *masks)))
