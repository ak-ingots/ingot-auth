"""
The groups of the users, each granting permissions. The code is their
source, the first: an application declares them as slots of
:class:`AuthGroupsUnit`, the name of the slot the name of the group::

    class AppGroupsUnit(AuthGroupsUnit):
        admins = Slot(AdminsGroup)

The core declares one, ``signed_in``, :class:`AuthSignedInGroup`, of every
signed-in user.
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
    "AuthSignedInGroup",
)

import hashlib
import json
import re
import typing as t

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import AuthListGroupsCommand
from .entities import AuthGroup, AuthSignedInGroup
from .errors import AuthGroupError, AuthGroupNotFoundError
from .items import AuthGroupInfo
from .operations import AuthListGroupsOperation
from .permissions import AuthGroupsPermissions

# a name is of the scripts and the memberships, for good
NAME_PATTERN: t.Final = re.compile(r"[a-z][a-z0-9_]*")


class AuthGroupsUnit(CliUnit):
    """
    The groups, ``signed_in`` here, of every signed-in user: whatever their
    source, they come by :meth:`get` and :meth:`get_all`. A name of a group
    is lowercase letters, digits and ``_``, checked when the class is
    created.
    """

    cli_name = "groups"
    cli_description = "The groups of the users."

    op_list = Factory(AuthListGroupsOperation)

    cmd_list = Slot(AuthListGroupsCommand)

    signed_in = Slot(AuthSignedInGroup)

    _digest: str

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

    @t.final
    def get_digest(self) -> str:
        """
        A digest of the groups and what each grants, computed once, as they
        change with a deploy only: the key of a caller in the cache holds it,
        so that a deploy changing them finds none of the callers formed
        before.
        """
        try:
            return self._digest
        except AttributeError:
            pass
        grants = sorted(
            (group.get_name(), sorted(group.get_permissions().items()))
            for group in self.get_all()
        )
        self._digest = hashlib.sha256(json.dumps(grants).encode()).hexdigest()
        return self._digest
