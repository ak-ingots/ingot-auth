"""The storage of the profiles in memory."""

__all__ = (
    "AuthMemoryAttrsStorage",
    "AuthMemoryIdentitiesStorage",
    "AuthMemoryProfilesStorage",
    "AuthMemorySecretsStorage",
    "AuthMemoryTagsStorage",
)

import typing as t

from ingots.puer import Slot

from ingot_auth.profiles import (
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
    AuthProfilesStorage,
)

from ..state import AuthMemoryStateMixin
from .attrs import AuthMemoryAttrsStorage
from .identities import AuthMemoryIdentitiesStorage
from .secrets import AuthMemorySecretsStorage
from .tags import AuthMemoryTagsStorage

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryProfilesStorage(AuthMemoryStateMixin, AuthProfilesStorage):
    """The storage of the profiles in memory."""

    tags = Slot(AuthMemoryTagsStorage)
    attrs = Slot(AuthMemoryAttrsStorage)
    identities = Slot(AuthMemoryIdentitiesStorage)
    secrets = Slot(AuthMemorySecretsStorage)

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._profiles: dict[str, AuthProfile] = {}

    @t.override
    async def _create(self, profile: AuthProfile) -> None:
        if profile.uid in self._profiles:
            raise AuthProfileConflictError.for_uid(profile.uid)
        self._profiles[profile.uid] = profile

    @t.override
    async def _get(self, uid: str) -> AuthProfile:
        try:
            return self._profiles[uid]
        except KeyError:
            raise AuthProfileNotFoundError.for_uid(uid) from None
