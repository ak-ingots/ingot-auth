"""The commands of the groups."""

__all__ = ("AuthListGroupsCommand",)

import typing as t

from ingots.defaults.operations import BaseOperationCommand

from .items import AuthGroupInfo
from .operations import AuthListGroupsOperation

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class AuthListGroupsCommand(BaseOperationCommand[None, tuple[AuthGroupInfo, ...]]):
    """
    Prints the groups, one a line: the name, then what it grants, a mask a
    domain, sorted by the domain: ``auth.access.members=3``.
    """

    project: "AuthProject"

    cli_name = "list"
    cli_description = "Prints the groups and what each grants."

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListGroupsOperation]":
        return self.project.auth.access.groups.op_list

    @t.override
    async def _run(self) -> None:
        for group in await self.run_operation(None):
            permissions = sorted(group.permissions.items())
            masks = (f"{domain}={mask}" for domain, mask in permissions)
            print("\t".join((group.name, *masks)))
