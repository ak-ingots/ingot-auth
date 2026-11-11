"""The identities in memory."""

__all__ = ("AuthMemoryIdentitiesStorage",)

import typing as t

from ingot_auth.storages import (
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    BaseAuthIdentitiesStorage,
)

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from ingots.puer import Project


class AuthMemoryIdentitiesStorage(AuthMemoryStateMixin, BaseAuthIdentitiesStorage):
    """The identities in memory, by the kind and the value."""

    def __init__(self, project: "Project") -> None:
        super().__init__(project)
        self._uids: dict[tuple[str, str], str] = {}

    @t.override
    async def _create(self, identity: AuthIdentity) -> None:
        key = (identity.kind, identity.value)
        if key in self._uids:
            raise AuthIdentityConflictError.for_kind(identity.kind)
        self._uids[key] = identity.uid

    @t.override
    async def _find_uid(self, kind: str, value: str) -> str:
        try:
            return self._uids[kind, value]
        except KeyError:
            raise AuthIdentityNotFoundError.for_kind(kind) from None
