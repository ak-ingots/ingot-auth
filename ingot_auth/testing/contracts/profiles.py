"""
The contracts of the storage of the profiles themselves, their identities and
the secrets of these.
"""

__all__ = (
    "AuthIdentitiesStorageContract",
    "AuthProfileValuesStorageContract",
    "AuthProfilesStorageContract",
    "AuthSecretsStorageContract",
)

import asyncio
import datetime
import decimal
import typing as t

from ingot_auth.storages import (
    AuthAttrValue,
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
    AuthProfileValues,
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
        await identities.create(
            AuthIdentity(kind="email", value="a@b.c", profile_uid="a1")
        )
        self.assertEqual(await identities.find_uid("email", "a@b.c"), "a1")

    async def test_an_identifier_is_bound_once_a_kind(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        await identities.create(
            AuthIdentity(kind="email", value="alice", profile_uid="a1")
        )
        await identities.create(
            AuthIdentity(kind="nickname", value="alice", profile_uid="a1")
        )
        with self.assertRaises(AuthIdentityConflictError) as error:
            await identities.create(
                AuthIdentity(kind="email", value="alice", profile_uid="b2")
            )
        self.assertEqual(error.exception.kind, "email")
        self.assertEqual(await identities.find_uid("email", "alice"), "a1")

    async def test_an_unbound_identifier_is_not_found(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        await identities.create(
            AuthIdentity(kind="email", value="a@b.c", profile_uid="a1")
        )
        for kind, value in (("email", "b@b.c"), ("phone", "a@b.c")):
            with self.assertRaises(AuthIdentityNotFoundError) as error:
                await identities.find_uid(kind, value)
            self.assertEqual(error.exception.kind, kind)

    async def test_of_concurrent_bindings_of_an_identifier_one_wins(self) -> None:
        identities = self.project.auth.storage.profiles.identities
        results = await asyncio.gather(
            *(
                identities.create(
                    AuthIdentity(kind="email", value="a", profile_uid=uid)
                )
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


class AuthProfileValuesStorageContract(BaseAuthContract):
    """The values of the profiles of a storage: the tags, those of the attributes."""

    async def test_a_profile_of_none_has_empty_values(self) -> None:
        values = await self.project.auth.storage.profiles.values.get("a1")
        self.assertEqual(values, AuthProfileValues())

    async def test_the_values_are_kept_each_set_apart(self) -> None:
        values = self.project.auth.storage.profiles.values
        attr_values: dict[int, AuthAttrValue] = {
            1: True,
            2: 7,
            3: decimal.Decimal("1.50"),
            4: NOW,
            5: "x",
        }
        await values.set_tags("a1", frozenset({2, 1}))
        await values.set_attr_values("a1", attr_values)
        await values.set_tags("b2", frozenset({3}))
        self.assertEqual(
            await values.get("a1"),
            AuthProfileValues(tag_uids=frozenset({1, 2}), attr_values=attr_values),
        )
        self.assertEqual(
            await values.get("b2"), AuthProfileValues(tag_uids=frozenset({3}))
        )

    async def test_a_set_replaces_the_whole_set(self) -> None:
        values = self.project.auth.storage.profiles.values
        await values.set_tags("a1", frozenset({1, 2}))
        await values.set_attr_values("a1", {1: "x", 2: "y"})
        await values.set_tags("a1", frozenset({3}))
        await values.set_attr_values("a1", {})
        self.assertEqual(
            await values.get("a1"), AuthProfileValues(tag_uids=frozenset({3}))
        )
