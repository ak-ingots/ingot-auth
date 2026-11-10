"""
The groups of the users, each granting permissions. The code is their
source, the first: an application declares them as slots of
:class:`AuthGroupsUnit`, the name of the slot the name of the group::

    class AppGroupsUnit(AuthGroupsUnit):
        admins = Slot(AdminsGroup)
"""

__all__ = (
    "AuthGroup",
    "AuthGroupError",
    "AuthGroupInfo",
    "AuthGroupNotFoundError",
    "AuthGroupsUnit",
    "AuthGroupsPermissions",
    "AuthListGroupsOperation",
    "AuthListGroupsCommand",
)

import re
import typing as t

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import AuthListGroupsCommand
from .entities import AuthGroup
from .errors import AuthGroupError, AuthGroupNotFoundError
from .items import AuthGroupInfo
from .operations import AuthListGroupsOperation
from .permissions import AuthGroupsPermissions

# a name is of the scripts and the memberships, for good
NAME_PATTERN: t.Final = re.compile(r"[a-z][a-z0-9_]*")


class AuthGroupsUnit(CliUnit):
    """
    The groups, none here: whatever their source, they come by :meth:`get`
    and :meth:`get_all`. A name of a group is lowercase letters, digits and
    ``_``, checked when the class is created.
    """

    cli_name = "groups"
    cli_description = "The groups of the users."

    op_list = Factory(AuthListGroupsOperation)

    cmd_list = Slot(AuthListGroupsCommand)

    @t.override
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        for name, _ in cls.slots_iter(AuthGroup):
            if NAME_PATTERN.fullmatch(name) is None:
                raise TypeError(
                    f"{cls.__qualname__}.{name}: a name of a group is lowercase "
                    f"letters, digits and '_'"
                )

    @t.final
    def get_all(self) -> tuple[AuthGroup, ...]:
        """The groups, in the order of their slots."""
        return tuple(
            self.slots_find_entity(name, AuthGroup)
            for name, _ in type(self).slots_iter(AuthGroup)
        )

    @t.final
    def get(self, name: str) -> AuthGroup:
        """
        The group of a name.

        :raises AuthGroupNotFoundError: no group has the name.
        """
        try:
            return self.slots_find_entity(name, AuthGroup)
        except LookupError:
            raise AuthGroupNotFoundError.for_name(name) from None
