"""The memberships in memory."""

__all__ = ("AuthMemoryMembersStorage",)

import typing as t

from ingot_auth.access.members import AuthMembership, BaseAuthMembersStorage

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryMembersStorage(AuthMemoryStateMixin, BaseAuthMembersStorage):
    """The memberships in memory, a set of the pairs of a group and a uid."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._memberships: set[tuple[str, str]] = set()

    @t.override
    async def _add(self, membership: AuthMembership) -> None:
        self._memberships.add((membership.group, membership.uid))

    @t.override
    async def _remove(self, membership: AuthMembership) -> None:
        self._memberships.discard((membership.group, membership.uid))

    @t.override
    async def _get_uids(self, group: str) -> tuple[str, ...]:
        return tuple(sorted(u for g, u in self._memberships if g == group))

    @t.override
    async def _get_groups(self, uid: str) -> tuple[str, ...]:
        return tuple(sorted(g for g, u in self._memberships if u == uid))
