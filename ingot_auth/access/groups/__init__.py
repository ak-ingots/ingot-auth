"""
The groups of the users, each granting permissions. The code is their
source, the first: a group is a slot of a unit of its domain, an
:class:`AuthGroupsOwner`, prefixed ``grp_``, its name its full name::

    class ShopBuyersGroup(AuthGroup):
        parent: "ShopUnit"

        @t.override
        def _get_permissions(self) -> Permissions:
            permissions = self.parent.permissions
            return super()._get_permissions() | permissions(permissions.flags.CAN_BUY)


    class ShopUnit(AuthGroupsOwner, OperationsOwner, Unit):
        grp_buyers = Slot(ShopBuyersGroup)  # the group shop.grp_buyers

The core declares two in the auth, ``auth.grp_anonymous``,
:class:`AuthAnonymousGroup`, of every caller that tells no one, and
``auth.grp_signed_in``, :class:`AuthSignedInGroup`, of every signed-in user,
and those of the work of its registries in the profiles and the sessions.
:class:`AuthGroupsUnit` finds them, whatever their source.
"""

__all__ = (
    "AuthAnonymousGroup",
    "AuthGroup",
    "AuthGroupError",
    "AuthGroupInfo",
    "AuthGroupNotFoundError",
    "AuthGroupsOwner",
    "AuthGroupsUnit",
    "AuthGroupsPermissions",
    "AuthListGroupsOperation",
    "AuthListGroupsCommand",
    "AuthSignedInGroup",
)

import hashlib
import json
import typing as t

from ingots.defaults.operations import OperationsOwner, PermissionsSlot
from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import AuthListGroupsCommand
from .entities import AuthAnonymousGroup, AuthGroup, AuthSignedInGroup
from .errors import AuthGroupError, AuthGroupNotFoundError
from .items import AuthGroupInfo
from .operations import AuthListGroupsOperation
from .owners import AuthGroupsOwner, find_group_names
from .permissions import AuthGroupsPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGroupsUnit(OperationsOwner, CliUnit):
    """
    The groups of the project, whatever their source, by :meth:`get` and
    :meth:`get_all`: those of the code in the slots of the units of their
    domains, :class:`AuthGroupsOwner`, found once by a walk from the project
    down the owners. It holds none: a group in a slot of it is refused when
    the class is created, as it belongs to its domain.
    """

    cli_name = "groups"
    cli_description = "The groups of the users."

    project: "AuthProject"

    permissions = PermissionsSlot(AuthGroupsPermissions)

    op_list = Factory(AuthListGroupsOperation)

    cmd_list = Slot(AuthListGroupsCommand)

    _names: tuple[str, ...]
    _digest: str

    @t.override
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        super().__init_subclass__(**kwargs)
        for name, _ in cls.slots_iter(AuthGroup):
            raise TypeError(
                f"{cls.__qualname__}.{name}: a group is declared in a unit of "
                f"its domain, an AuthGroupsOwner"
            )

    @t.final
    def get_all(self) -> tuple[AuthGroup, ...]:
        """The groups, in the order of the walk."""
        project = self.project
        return tuple(
            project.slots_find_entity(name, AuthGroup) for name in self.get_names()
        )

    @t.final
    def get(self, name: str) -> AuthGroup:
        """
        The group of a name, its full name.

        :raises AuthGroupNotFoundError: no group has the name.
        """
        if name not in self.get_names():
            raise AuthGroupNotFoundError.for_name(name)
        return self.project.slots_find_entity(name, AuthGroup)

    @t.final
    def get_names(self) -> tuple[str, ...]:
        """
        The names of the groups, their full names from the project, found
        once, as they change with a deploy only.
        """
        try:
            return self._names
        except AttributeError:
            pass
        self._names = find_group_names(type(self.project))
        return self._names

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
