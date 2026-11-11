"""The contract of the storage of the access: the memberships."""

__all__ = ("AuthMembersStorageContract",)

import typing as t

from ingot_auth.storages import AuthMembership

from .base import BaseAuthContract

if t.TYPE_CHECKING:
    from ingot_auth.storages import BaseAuthMembersStorage


class AuthMembersStorageContract(BaseAuthContract):
    """The memberships of a storage, many to many."""

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.storage: BaseAuthMembersStorage = self.project.auth.storage.access.members

    async def test_there_are_no_members_at_first(self) -> None:
        self.assertEqual(await self.storage.get_uids("admins"), ())
        self.assertEqual(await self.storage.get_groups("a1"), ())

    async def test_the_members_come_by_group_and_by_uid_sorted(self) -> None:
        for group, uid in (("editors", "b2"), ("admins", "b2"), ("editors", "a1")):
            await self.storage.add(AuthMembership(group=group, uid=uid))
        self.assertEqual(await self.storage.get_uids("editors"), ("a1", "b2"))
        self.assertEqual(await self.storage.get_uids("admins"), ("b2",))
        self.assertEqual(await self.storage.get_groups("b2"), ("admins", "editors"))
        self.assertEqual(await self.storage.get_groups("a1"), ("editors",))

    async def test_a_membership_is_kept_once(self) -> None:
        membership = AuthMembership(group="admins", uid="a1")
        await self.storage.add(membership)
        await self.storage.add(membership)
        self.assertEqual(await self.storage.get_uids("admins"), ("a1",))

    async def test_a_removed_membership_is_gone_alone(self) -> None:
        await self.storage.add(AuthMembership(group="admins", uid="a1"))
        await self.storage.add(AuthMembership(group="editors", uid="a1"))
        await self.storage.remove(AuthMembership(group="admins", uid="a1"))
        self.assertEqual(await self.storage.get_groups("a1"), ("editors",))
        self.assertEqual(await self.storage.get_uids("admins"), ())

    async def test_removing_a_membership_not_kept_is_no_error(self) -> None:
        await self.storage.remove(AuthMembership(group="admins", uid="a1"))
        self.assertEqual(await self.storage.get_uids("admins"), ())
