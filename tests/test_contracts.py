"""The contracts of the addon, on the storage in memory."""

import unittest

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.project import AuthProject
from ingot_auth.testing.contracts import (
    AuthAttemptsCacheContract,
    AuthAttrsStorageContract,
    AuthIdentitiesStorageContract,
    AuthMembersStorageContract,
    AuthProfilesStorageContract,
    AuthSecretsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthSessionPresetsStorageContract,
    AuthSignUpRecordsStorageContract,
    AuthStorageTransactionsContract,
    AuthTagsStorageContract,
)


class MemoryStorageMixin:
    async def create_project(self) -> AuthProject:
        return AuthMemoryProject()


class MemoryTagsStorageTestCase(
    MemoryStorageMixin, AuthTagsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


class MemoryAttrsStorageTestCase(
    MemoryStorageMixin, AuthAttrsStorageContract, unittest.IsolatedAsyncioTestCase
):
    pass


class MemorySessionAttrsStorageTestCase(
    MemoryStorageMixin,
    AuthSessionAttrsStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemorySessionPresetsStorageTestCase(
    MemoryStorageMixin,
    AuthSessionPresetsStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemoryProfilesStorageTestCase(
    MemoryStorageMixin,
    AuthProfilesStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemoryIdentitiesStorageTestCase(
    MemoryStorageMixin,
    AuthIdentitiesStorageContract,
    AuthMembersStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemorySecretsStorageTestCase(
    MemoryStorageMixin,
    AuthSecretsStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemorySignUpRecordsStorageTestCase(
    MemoryStorageMixin,
    AuthSignUpRecordsStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemoryMembersStorageTestCase(
    MemoryStorageMixin,
    AuthMembersStorageContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass


class MemoryAttemptsCacheTestCase(
    MemoryStorageMixin, AuthAttemptsCacheContract, unittest.IsolatedAsyncioTestCase
):
    pass


class MemoryStorageTransactionsTestCase(
    MemoryStorageMixin,
    AuthStorageTransactionsContract,
    unittest.IsolatedAsyncioTestCase,
):
    pass
