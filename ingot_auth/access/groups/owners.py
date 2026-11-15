"""The units owning the groups, and the walk finding them."""

__all__ = ("AuthGroupsOwner", "find_group_names")

import typing as t

from ingots.puer import Slot, Unit

from .entities import AuthGroup

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingots.puer import SlotsOwner


class AuthGroupsOwner(Unit):
    """
    A unit owning groups, of its domain, in its slots prefixed ``grp_``::

        class ShopUnit(AuthGroupsOwner):
            grp_buyers = Slot(ShopBuyersGroup)

    The groups of a project are found in the units of their domains, as its
    commands are in its units of the command line: by a walk from the
    project down the owners alone, :func:`find_group_names`. A plain unit
    and everything in it stay out of the groups.
    """


def find_group_names(project_cls: "type[SlotsOwner]") -> tuple[str, ...]:
    """
    Internal: the names of the groups of a project class, their full names,
    in the order of the walk, depth first down the owners of groups.
    """
    return tuple(path for path, _ in walk_groups(project_cls))


def walk_groups(
    owner_cls: "type[SlotsOwner]",
) -> "Iterator[tuple[str, type[AuthGroup]]]":
    """
    Internal: the classes of the groups under a class, in its slots and,
    depth first, in those of the owners of groups in it, with their dotted
    paths, in declaration order.
    """
    for name, slot in owner_cls.slots_iter():
        if issubclass(slot.cls, AuthGroup) and isinstance(slot, Slot):
            yield name, slot.cls
        elif issubclass(slot.cls, AuthGroupsOwner):
            for path, cls in walk_groups(slot.cls):
                yield f"{name}.{path}", cls
