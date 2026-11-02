"""The profiles in memory."""

__all__ = ("AuthMemoryProfilesStorage",)

import typing as t

from ingot_auth.profile.profiles import (
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileNotFoundError,
    BaseAuthProfilesStorage,
)

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryProfilesStorage(AuthMemoryStateMixin, BaseAuthProfilesStorage):
    """The profiles in memory."""

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
