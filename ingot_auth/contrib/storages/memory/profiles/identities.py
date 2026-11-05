"""The identities in memory."""

__all__ = ("AuthMemoryIdentitiesStorage",)

import typing as t

from ingot_auth.profiles.identities import (
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    BaseAuthIdentitiesStorage,
)

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryIdentitiesStorage(AuthMemoryStateMixin, BaseAuthIdentitiesStorage):
    """The identities in memory, by the method and the subject."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._uids: dict[tuple[str, str], str] = {}

    @t.override
    async def _create(self, identity: AuthIdentity) -> None:
        key = (identity.method, identity.subject)
        if key in self._uids:
            raise AuthIdentityConflictError.for_method(identity.method)
        self._uids[key] = identity.uid

    @t.override
    async def _find_uid(self, method: str, subject: str) -> str:
        try:
            return self._uids[method, subject]
        except KeyError:
            raise AuthIdentityNotFoundError.for_method(method) from None
