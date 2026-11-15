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
    "AuthActivitiesStorageContract",
    "AuthAttemptsCacheContract",
    "AuthAttrsStorageContract",
    "AuthCallersCacheContract",
    "AuthIdentitiesStorageContract",
    "AuthMailerContract",
    "AuthMembersStorageContract",
    "AuthProfileValuesStorageContract",
    "AuthProfilesStorageContract",
    "AuthSecretsStorageContract",
    "AuthSessionAttrsStorageContract",
    "AuthSessionPresetsStorageContract",
    "AuthSessionsCacheContract",
    "AuthSessionsStorageContract",
    "AuthSignUpRecordsStorageContract",
    "AuthStorageTransactionsContract",
    "AuthTagsStorageContract",
)

from .activities import AuthActivitiesStorageContract
from .access import AuthMembersStorageContract
from .cache import (
    AuthAttemptsCacheContract,
    AuthCallersCacheContract,
    AuthSessionsCacheContract,
)
from .mailer import AuthMailerContract
from .profiles import (
    AuthIdentitiesStorageContract,
    AuthProfileValuesStorageContract,
    AuthProfilesStorageContract,
    AuthSecretsStorageContract,
)
from .sessions import AuthSessionsStorageContract
from .sign_up import AuthSignUpRecordsStorageContract
from .storage import (
    AuthAttrsStorageContract,
    AuthSessionAttrsStorageContract,
    AuthSessionPresetsStorageContract,
    AuthTagsStorageContract,
)
from .transactions import AuthStorageTransactionsContract
