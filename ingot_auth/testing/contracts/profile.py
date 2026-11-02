"""The contracts of the storage of the profiles themselves and their identities."""

__all__ = ("AuthIdentitiesStorageContract", "AuthProfilesStorageContract")

import asyncio
import datetime
import typing as t

from ingot_auth.profile.identities import (
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
)
from ingot_auth.profile.profiles import (
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
)

from .base import BaseAuthContract

# a time as a storage keeps it: in UTC, to the millisecond
NOW: t.Final = datetime.datetime(2026, 11, 2, 9, 30, 15, 123000, datetime.UTC)


class AuthProfilesStorageContract(BaseAuthContract):
    """The profiles of a storage."""

    async def test_a_profile_is_given_as_created(self) -> None:
        profile = AuthProfile(uid="a1", created_at=NOW)
        await self.project.auth.storage.profile.profiles.create(profile)
        self.assertEqual(
            await self.project.auth.storage.profile.profiles.get("a1"), profile
        )

    async def test_a_uid_is_taken_once(self) -> None:
        profiles = self.project.auth.storage.profile.profiles
        await profiles.create(AuthProfile(uid="a1", created_at=NOW))
        with self.assertRaises(AuthProfileConflictError) as error:
            await profiles.create(AuthProfile(uid="a1", created_at=NOW))
        self.assertEqual(error.exception.uid, "a1")

    async def test_an_unknown_uid_is_not_found(self) -> None:
        with self.assertRaises(AuthProfileNotFoundError) as error:
            await self.project.auth.storage.profile.profiles.get("a1")
        self.assertEqual(error.exception.uid, "a1")


class AuthIdentitiesStorageContract(BaseAuthContract):
    """The identities of a storage."""

    async def test_a_subject_gives_its_uid(self) -> None:
        identities = self.project.auth.storage.profile.identities
        await identities.create(AuthIdentity(method="mail", subject="a@b.c", uid="a1"))
        self.assertEqual(await identities.find_uid("mail", "a@b.c"), "a1")

    async def test_a_subject_is_bound_once_a_method(self) -> None:
        identities = self.project.auth.storage.profile.identities
        await identities.create(AuthIdentity(method="mail", subject="a@b.c", uid="a1"))
        await identities.create(AuthIdentity(method="code", subject="a@b.c", uid="a1"))
        with self.assertRaises(AuthIdentityConflictError) as error:
            await identities.create(
                AuthIdentity(method="mail", subject="a@b.c", uid="b2")
            )
        self.assertEqual(error.exception.method, "mail")
        self.assertEqual(await identities.find_uid("mail", "a@b.c"), "a1")

    async def test_an_unbound_subject_is_not_found(self) -> None:
        identities = self.project.auth.storage.profile.identities
        await identities.create(AuthIdentity(method="mail", subject="a@b.c", uid="a1"))
        for method, subject in (("mail", "b@b.c"), ("code", "a@b.c")):
            with self.assertRaises(AuthIdentityNotFoundError) as error:
                await identities.find_uid(method, subject)
            self.assertEqual(error.exception.method, method)

    async def test_of_concurrent_bindings_of_a_subject_one_wins(self) -> None:
        identities = self.project.auth.storage.profile.identities
        results = await asyncio.gather(
            *(
                identities.create(AuthIdentity(method="mail", subject="a", uid=uid))
                for uid in ("a1", "b2")
            ),
            return_exceptions=True,
        )
        conflicts = [r for r in results if isinstance(r, AuthIdentityConflictError)]
        self.assertEqual(len(conflicts), 1, results)
