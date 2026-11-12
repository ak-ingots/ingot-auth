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
from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.mongodb import (
    AuthMongoDbSessionsStorage,
    AuthMongoDbStorage,
)
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpPermissions,
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
    AuthSecretsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthSessionPresetsStorageContract,
    AuthSessionsStorageContract,
    AuthSignUpRecordsStorageContract,
    AuthStorageTransactionsContract,
    AuthTagsStorageContract,
)
from ingot_auth.testing.contracts.sessions import create_session
from ingot_auth.testing.methods import (
    AuthTestingMethod,
    AuthTestingPermissions,
    AuthTestingStart,
)

PORT = os.environ.get("INGOT_AUTH_TEST_PORT")
SIGNING_UP: t.Final = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignUpPermissions.CAN_SIGN_UP, AuthTestingPermissions.CAN_SIGN_UP
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
    methods = Slot(TstMethodsUnit)


class TstProject(AuthProject, MongoDbProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)


if t.TYPE_CHECKING:
    TestCase: t.TypeAlias = unittest.IsolatedAsyncioTestCase
else:
    TestCase = object


class ServerMixin(TestCase):
    async def start(self) -> TstProject:
        project = TstProject()
        await project._configure()
        self.addAsyncCleanup(project._do_shut_down)
        return project

    async def create_project(self) -> AuthProject:
        self.enterContext(
            mock.patch.dict(
                os.environ,
                {
                    "INGOT_MONGODB_DEFAULT_HOST": "127.0.0.1",
                    "INGOT_MONGODB_DEFAULT_PORT": str(PORT),
                    "INGOT_MONGODB_DEFAULT_SERVER_SELECTION_TIMEOUT": "5",
                    "INGOT_IS_PRINT_CONFIGS": "off",
                },
                clear=True,
            )
        )
        # the logging is not under test: keep the handlers of the test run
        self.enterContext(mock.patch("logging.config.dictConfig"))
        project = await self.start()
        client = await project.mongodb.clients.default
        await client.client.drop_database("ingot_auth")
        return project


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbTagsStorageTestCase(
    ServerMixin, AuthTagsStorageContract, unittest.IsolatedAsyncioTestCase
):
    async def test_the_items_outlive_the_project(self) -> None:
        tag = AuthTag(id=1, name="beta")
        await self.storage.create(tag)
        project = await self.start()
        self.assertEqual(await project.auth.storage.profiles.tags.get_all(), (tag,))


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbAttrsStorageTestCase(
    ServerMixin, AuthAttrsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionAttrsStorageTestCase(
    ServerMixin, AuthSessionAttrsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionPresetsStorageTestCase(
    ServerMixin, AuthSessionPresetsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbStorageTransactionsTestCase(
    ServerMixin, AuthStorageTransactionsContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbProfilesStorageTestCase(
    ServerMixin, AuthProfilesStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbIdentitiesStorageTestCase(
    ServerMixin, AuthIdentitiesStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSecretsStorageTestCase(
    ServerMixin, AuthSecretsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSignUpRecordsStorageTestCase(
    ServerMixin, AuthSignUpRecordsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbMembersStorageTestCase(
    ServerMixin, AuthMembersStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSessionsStorageTestCase(
    ServerMixin, AuthSessionsStorageContract, unittest.IsolatedAsyncioTestCase
):
    async def test_a_session_of_0_1_0_is_seen_at_its_sign_in(self) -> None:
        sessions = t.cast(
            AuthMongoDbSessionsStorage, self.project.auth.storage.sessions
        )
        await sessions.open(create_session())
        collection = await sessions._mongodb_get_collection()
        await collection.update_one({"_id": "s1"}, {"$unset": {"seen_at": ""}})
        session = await sessions.find("h1")
        self.assertEqual(session.seen_at, session.opened_at)


@unittest.skipUnless(PORT, "no MongoDB: run make integration")
class MongoDbSignUpTestCase(ServerMixin, unittest.IsolatedAsyncioTestCase):
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
