"""The records of the sign-ups in memory."""

__all__ = ("AuthMemorySignUpRecordsStorage",)

import typing as t

from ingot_auth.storages import (
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    BaseAuthSignUpRecordsStorage,
)

from ..state import AuthMemoryStateMixin


class AuthMemorySignUpRecordsStorage(
    AuthMemoryStateMixin, BaseAuthSignUpRecordsStorage
):
    """The records of the sign-ups in memory."""

    def __init__(self) -> None:
        super().__init__()
        self._records: dict[str, AuthSignUpRecord] = {}

    @t.override
    async def _add(self, record: AuthSignUpRecord) -> None:
        self._records[record.uid] = record

    @t.override
    async def _get(self, uid: str) -> AuthSignUpRecord:
        try:
            return self._records[uid]
        except KeyError:
            raise AuthSignUpRecordNotFoundError.for_uid(uid) from None
