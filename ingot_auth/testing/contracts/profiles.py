"""
The contracts of the storage of the profiles themselves, their identities and
the secrets of these.
"""

__all__ = (
    "AuthIdentitiesStorageContract",
    "AuthProfilesStorageContract",
    "AuthSecretsStorageContract",
)

import asyncio
import datetime
import typing as t

from ingot_auth.storages import (
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
    AuthSecretNotFoundError,
)

from .base import BaseAuthContract

# a time as a storage keeps it: in UTC, to the millisecond
NOW: t.Final = datetime.datetime(2026, 11, 2, 9, 30, 15, 123000, datetime.UTC)


class AuthProfilesStorageContract(BaseAuthContract):
    """The profiles of a storage."""

    async def test_a_profile_is_given_as_created(self) -> None:
        profile = AuthProfile(uid="a1", created_at=NOW)
        await self.project.auth.storage.profiles.create(profile)
        self.assertEqual(await self.project.auth.storage.profiles.get("a1"), profile)

    async def test_a_uid_is_taken_once(self) -> None:
        profiles = self.project.auth.storage.profiles
        await profiles.create(AuthProfile(uid="a1", created_at=NOW))
        with self.assertRaises(AuthProfileConflictError) as error:
            await profiles.create(AuthProfile(uid="a1", created_at=NOW))
        self.assertEqual(error.exception.uid, "a1")

    async def test_an_unknown_uid_is_not_found(self) -> None:
        with self.assertRaises(AuthProfileNotFoundError) as error:
            await self.project.auth.storage.profiles.get("a1")
        self.assertEqual(error.exception.uid, "a1")


class AuthIdentitiesStorageContract(BaseAuthContract):
    """The identities of a storage."""

    async def test_an_identifier_gives_its_uid(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        await identities.create(AuthIdentity(kind="email", value="a@b.c", uid="a1"))
        self.assertEqual(await identities.find_uid("email", "a@b.c"), "a1")

    async def test_an_identifier_is_bound_once_a_kind(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        await identities.create(AuthIdentity(kind="email", value="alice", uid="a1"))
        await identities.create(AuthIdentity(kind="nickname", value="alice", uid="a1"))
        with self.assertRaises(AuthIdentityConflictError) as error:
            await identities.create(AuthIdentity(kind="email", value="alice", uid="b2"))
        self.assertEqual(error.exception.kind, "email")
        self.assertEqual(await identities.find_uid("email", "alice"), "a1")

    async def test_an_unbound_identifier_is_not_found(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        await identities.create(AuthIdentity(kind="email", value="a@b.c", uid="a1"))
        for kind, value in (("email", "b@b.c"), ("phone", "a@b.c")):
            with self.assertRaises(AuthIdentityNotFoundError) as error:
                await identities.find_uid(kind, value)
            self.assertEqual(error.exception.kind, kind)

    async def test_of_concurrent_bindings_of_an_identifier_one_wins(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        results = await asyncio.gather(
            *(
                identities.create(AuthIdentity(kind="email", value="a", uid=uid))
                for uid in ("a1", "b2")
            ),
            return_exceptions=True,
        )
        conflicts = [r for r in results if isinstance(r, AuthIdentityConflictError)]
        self.assertEqual(len(conflicts), 1, results)


class AuthSecretsStorageContract(BaseAuthContract):
    """The secrets of a storage, one a profile."""

    async def test_a_secret_is_given_as_put(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        await secrets.put("a1", "hash-1")
        await secrets.put("b2", "hash-2")
        self.assertEqual(await secrets.get("a1"), "hash-1")
        self.assertEqual(await secrets.get("b2"), "hash-2")

    async def test_a_secret_put_again_replaces_the_old(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        await secrets.put("a1", "hash-1")
        await secrets.put("a1", "hash-2")
        self.assertEqual(await secrets.get("a1"), "hash-2")

    async def test_a_profile_with_no_secret_is_not_found(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        await secrets.put("a1", "hash-1")
        with self.assertRaises(AuthSecretNotFoundError) as error:
            await secrets.get("b2")
        self.assertEqual(error.exception.uid, "b2")
