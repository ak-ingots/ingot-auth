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
from ingot_pymongo.logging import MongoDbLogging
from ingot_pymongo.settings import MongoDbSettings
from ingot_pymongo.settings.configs import MongoDbConfigs
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.storages.mongodb import AuthMongoDbStorage
from ingot_auth.logging import AuthLogging
from ingot_auth.profile.tags import AuthTag
from ingot_auth.settings import AuthSettings
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.testing.contracts import (
    AuthAttrsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthSessionPresetsStorageContract,
    AuthTagsStorageContract,
)

PORT = os.environ.get("INGOT_AUTH_TEST_PORT")


class TstConfigs(AuthConfigs, MongoDbConfigs):
    pass


class TstSettings(AuthSettings, MongoDbSettings):
    configs = Slot(TstConfigs)


class TstLogging(AuthLogging, MongoDbLogging):
    project: "TstProject"


class TstAuth(AuthUnit):
    storage = Slot(AuthMongoDbStorage)


class TstProject(AuthProject, MongoDbProject):
    settings = Slot(TstSettings)
    logging = Slot(TstLogging)
    auth = Slot(TstAuth)


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
                    "INGOT_MONGODB_DEFAULT_USER": "ingot",
                    "INGOT_MONGODB_DEFAULT_PASSWORD": "ingot",
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
        self.assertEqual(await project.auth.storage.profile.tags.get_all(), (tag,))


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
