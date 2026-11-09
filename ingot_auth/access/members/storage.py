"""The storage of the memberships."""

__all__ = ("BaseAuthMembersStorage",)

import abc
import typing as t

from ingots.puer import Entity

from .items import AuthMembership


class BaseAuthMembersStorage(Entity):
    """
    The memberships, each once: what a backend implements. It takes any
    group and uid: the operations look whether they are there.
    """

    @t.final
    async def add(self, membership: AuthMembership) -> None:
        """Keeps a membership; one kept already stays as it is."""
        await self._add(membership)

    @t.final
    async def remove(self, membership: AuthMembership) -> None:
        """Forgets a membership; one not kept is no error."""
        await self._remove(membership)

    @t.final
    async def get_uids(self, group: str) -> tuple[str, ...]:
        """The uids of the members of a group, sorted."""
        return await self._get_uids(group)

    @t.final
    async def get_groups(self, uid: str) -> tuple[str, ...]:
        """The names of the groups of a uid, sorted."""
        return await self._get_groups(uid)

    @abc.abstractmethod
    async def _add(self, membership: AuthMembership) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._add")

    @abc.abstractmethod
    async def _remove(self, membership: AuthMembership) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._remove")

    @abc.abstractmethod
    async def _get_uids(self, group: str) -> tuple[str, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_uids")

    @abc.abstractmethod
    async def _get_groups(self, uid: str) -> tuple[str, ...]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_groups")
