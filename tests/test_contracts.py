"""The contracts of the addon, on the storage in memory."""

import unittest

from ingot_auth.__main__ import AuthMemoryProject
from ingot_auth.testing.contracts import (
    AuthAttrsStorageContract,
    AuthTagsStorageContract,
)
from ingot_auth.project import AuthProject


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
