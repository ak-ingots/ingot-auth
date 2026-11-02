"""
The contracts of the addon (ADRs 0005, 0010 of the ecosystem): the guarantees of its
public API, as tests a consumer runs on its own classes. Nothing imports them at
runtime. A test case takes a contract and tells what to run it on::

    class AppTagsStorageTestCase(
        AuthTagsStorageContract, unittest.IsolatedAsyncioTestCase
    ):
        async def create_project(self) -> AuthProject:
            ...
"""

__all__ = (
    "AuthAttrsStorageContract",
    "AuthSessionAttrsStorageContract",
    "AuthTagsStorageContract",
)

from .storage import (
    AuthAttrsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthTagsStorageContract,
)
