"""
The storage in MongoDB against a real server: ``make integration``, ``coverage``
and ``installed-test`` start the one of ``docker-compose.yml`` and set
``INGOT_AUTH_TEST_PORT``; skipped without it.
"""

import os
import typing as t
import unittest
from unittest import mock

from ingot_pymongo import MongoDbProject
from ingot_pymongo.logging import MongoDbLoggingUnit
from ingot_pymongo.settings import MongoDbSettingsUnit
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingots.defaults.operations import Caller
from ingots.puer import Slot
from ingots.testing import ProjectFixture, ProjectTestCase

from ingot_auth.__main__ import AuthMemorySessionsUnit
from ingot_auth import AuthProject
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.mongodb import AuthMongoDbStorage
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpUnit,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from ingot_auth.sign_up.operations import BaseAuthSignUpOperation
from ingot_auth.storages import (
    AuthIdentityNotFoundError,
    AuthSecretNotFoundError,
    AuthTag,
)
from ingot_auth.testing.contracts import (
    AuthAttrsStorageContract,
    AuthIdentitiesStorageContract,
    AuthMembersStorageContract,
    AuthProfilesStorageContract,
    AuthActivitiesStorageContract,
    AuthProfileValuesStorageContract,
    AuthSecretsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthSessionPresetsStorageContract,
    AuthSessionsStorageContract,
    AuthSignUpRecordsStorageContract,
    AuthStorageTransactionsContract,
    AuthTagsStorageContract,
)
from ingot_auth.testing.methods import (
    AuthTestingMethod,
    AuthTestingStart,
)

from tests import masks

PORT = os.environ.get("INGOT_AUTH_TEST_PORT")
SIGNING_UP: t.Final = Caller(
    uid="anonymous",
    permissions=masks(
        AuthSignUpUnit.Flags.CAN_SIGN_UP, AuthTestingMethod.Flags.CAN_SIGN_UP
    ),
)


class TstConfigs(AuthConfigs, MongoDbConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit, MongoDbSettingsUnit):
    configs = Slot(TstConfigs)


class TstLoggingUnit(AuthLoggingUnit, MongoDbLoggingUnit):
    project: "TstProject"


class TstMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class TstAuthUnit(AuthUnit):
    storage = Slot(AuthMongoDbStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)
    methods = Slot(TstMethodsUnit)


class TstProject(AuthProject, MongoDbProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)


SERVER_CONFIGS: t.Final = {
    "MONGODB_DEFAULT_HOST": "127.0.0.1",
    "MONGODB_DEFAULT_PORT": str(PORT),
    "MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT": "5",
}


class ServerMixin:
    """The server of the tests, its database empty for each."""

    server = ProjectFixture(TstProject, configs=SERVER_CONFIGS)

    async def create_project(self) -> AuthProject:
        client = await self.server.mongodb.clients.default
        await client.client.drop_database("ingot_auth")
        return self.server


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbTagsStorageTestCase(ServerMixin, AuthTagsStorageContract, ProjectTestCase):
    other = ProjectFixture(TstProject, configs=SERVER_CONFIGS)

    async def test_the_items_outlive_the_project(self) -> None:
        tag = AuthTag(uid=1, name="beta")
        await self.storage.create(tag)
        storage = self.other.auth.storage
        self.assertEqual(await storage.profiles.tags.get_all(), (tag,))


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbAttrsStorageTestCase(
    ServerMixin, AuthAttrsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionAttrsStorageTestCase(
    ServerMixin, AuthSessionAttrsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionPresetsStorageTestCase(
    ServerMixin, AuthSessionPresetsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbStorageTransactionsTestCase(
    ServerMixin, AuthStorageTransactionsContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbProfilesStorageTestCase(
    ServerMixin, AuthProfilesStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbIdentitiesStorageTestCase(
    ServerMixin, AuthIdentitiesStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbProfileValuesStorageTestCase(
    ServerMixin, AuthProfileValuesStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbActivitiesStorageTestCase(
    ServerMixin, AuthActivitiesStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSecretsStorageTestCase(
    ServerMixin, AuthSecretsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSignUpRecordsStorageTestCase(
    ServerMixin, AuthSignUpRecordsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbMembersStorageTestCase(
    ServerMixin, AuthMembersStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionsStorageTestCase(
    ServerMixin, AuthSessionsStorageContract, ProjectTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSignUpTestCase(ServerMixin, ProjectTestCase):
    """A sign-up on the storage in MongoDB: its end is one transaction."""

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = await self.create_project()

    async def sign_up(self, start: AuthTestingStart) -> AuthSignUpResult:
        return await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start,
            AuthStartSignUpParameters(method="testing", parameters=start),
            self.project.operations.create_metadata(SIGNING_UP),
        )

    async def test_a_sign_up_keeps_what_it_writes(self) -> None:
        result = await self.sign_up(AuthTestingStart(subject="a@b.c", secret="hash"))
        assert isinstance(result, AuthSignedUp)
        storage = self.project.auth.storage
        self.assertEqual(
            await storage.profiles.identities.find_uid("testing", "a@b.c"), result.uid
        )
        self.assertEqual(await storage.profiles.secrets.get(result.uid), "hash")
        profile = await storage.profiles.get(result.uid)
        record = await storage.sign_up.records.get(result.uid)
        self.assertEqual(record.signed_up_at, profile.created_at)

    async def test_a_sign_up_failing_midway_leaves_nothing(self) -> None:
        storage = self.project.auth.storage
        with (
            mock.patch.object(type(storage.profiles), "_create", side_effect=OSError),
            mock.patch.object(
                BaseAuthSignUpOperation, "_create_uid", return_value="a1"
            ),
        ):
            with self.assertRaises(OSError):
                await self.sign_up(AuthTestingStart(subject="a@b.c", secret="hash"))
        with self.assertRaises(AuthIdentityNotFoundError):
            await storage.profiles.identities.find_uid("testing", "a@b.c")
        with self.assertRaises(AuthSecretNotFoundError):
            await storage.profiles.secrets.get("a1")
        result = await self.sign_up(AuthTestingStart(subject="a@b.c"))
        self.assertIsInstance(result, AuthSignedUp)
