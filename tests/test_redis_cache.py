"""
The cache in Redis against a real server: ``make integration``, ``coverage``
and ``installed-test`` start the one of ``docker-compose.yml`` and set
``INGOT_AUTH_TEST_REDIS_PORT``; skipped without it.
"""

import dataclasses
import datetime
import os
import typing as t
import unittest

from ingot_redis import RedisProject
from ingot_redis.logging import RedisLoggingUnit
from ingot_redis.settings import RedisSettingsUnit
from ingot_redis.settings.configs import RedisConfigs
from ingots.puer import Slot
from ingots.testing import ProjectFixture, ProjectTestCase

from ingot_auth import AuthProject
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.redis import AuthRedisCache
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.logging import AuthLoggingUnit
from ingot_auth.methods import AuthMethodsUnit
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.storages import AuthSessionCloseReason
from ingot_auth.testing.contracts import (
    AuthAttemptsCacheContract,
    AuthCallersCacheContract,
    AuthSessionsCacheContract,
)
from ingot_auth.testing.contracts.sessions import create_session
from ingot_auth.testing.methods import AuthTestingMethod, AuthTestingState

PORT = os.environ.get("INGOT_AUTH_TEST_REDIS_PORT")


class TstConfigs(AuthConfigs, RedisConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit, RedisSettingsUnit):
    configs = Slot(TstConfigs)


class TstLoggingUnit(AuthLoggingUnit, RedisLoggingUnit):
    project: "TstProject"


class TstMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class TstAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthRedisCache)
    dispatcher = Slot(AuthMemoryDispatcher)
    methods = Slot(TstMethodsUnit)


class TstProject(AuthProject, RedisProject):
    settings = Slot(TstSettingsUnit)
    logging = Slot(TstLoggingUnit)
    auth = Slot(TstAuthUnit)


class ServerMixin:
    """The server of the tests, its database empty for each."""

    server = ProjectFixture(
        TstProject,
        configs={"REDIS_DEFAULT_HOST": "127.0.0.1", "REDIS_DEFAULT_PORT": str(PORT)},
    )

    async def create_project(self) -> AuthProject:
        client = await self.server.redis.clients.default
        await client.client.flushdb()
        return self.server


@unittest.skipUnless(PORT, "no Redis: run make integration")
class RedisAttemptsCacheTestCase(
    ServerMixin, AuthAttemptsCacheContract, ProjectTestCase
):
    async def test_the_state_is_kept_as_its_method_gives_it(self) -> None:
        attempts = self.project.auth.cache.attempts
        state = AuthTestingState(subject="al", code="123456", secret="s3cret")
        attempt = dataclasses.replace(self.create_attempt(), state=state)
        await attempts.put(attempt)
        self.assertEqual(await attempts.take("x"), attempt)

    async def test_an_attempt_is_json_under_the_prefix(self) -> None:
        await self.project.auth.cache.attempts.put(self.create_attempt())
        client = await self.server.redis.clients.default
        self.assertEqual(await client.client.keys(), [b"ingot_auth:attempt:x"])
        data = await client.client.get("ingot_auth:attempt:x")
        self.assertIn(b'"subject": "al"', t.cast(bytes, data))


@unittest.skipUnless(PORT, "no Redis: run make integration")
class RedisSessionsCacheTestCase(
    ServerMixin, AuthSessionsCacheContract, ProjectTestCase
):
    async def test_a_closed_session_is_got_as_put(self) -> None:
        sessions = self.project.auth.cache.sessions
        now = datetime.datetime.now(datetime.UTC)
        session = dataclasses.replace(
            create_session(),
            closed_at=now,
            close_reason=AuthSessionCloseReason.SIGNED_OUT,
        )
        await sessions.put(session, now + datetime.timedelta(seconds=60))
        self.assertEqual(await sessions.get("h1"), session)


@unittest.skipUnless(PORT, "no Redis: run make integration")
class RedisCallersCacheTestCase(ServerMixin, AuthCallersCacheContract, ProjectTestCase):
    pass


class StateTestCase(unittest.TestCase):
    def test_a_state_comes_back_from_its_plain_values(self) -> None:
        project = TstProject()
        testing = project.auth.methods.testing
        for secret in (None, "s3cret"):
            state = AuthTestingState(subject="al", code="1", secret=secret)
            self.assertEqual(testing.load_state(testing.dump_state(state)), state)
