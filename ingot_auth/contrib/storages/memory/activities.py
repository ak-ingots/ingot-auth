"""The activity log in memory."""

__all__ = ("AuthMemoryActivitiesStorage",)

import typing as t

from ingot_auth.storages import (
    AuthActivityQuery,
    AuthActivityRecord,
    BaseAuthActivitiesStorage,
)

from .state import AuthMemoryStateMixin


class AuthMemoryActivitiesStorage(AuthMemoryStateMixin, BaseAuthActivitiesStorage):
    """The activity log in memory, the records in the order they came."""

    def __init__(self) -> None:
        super().__init__()
        self._records: list[AuthActivityRecord] = []

    @t.override
    async def _append(self, record: AuthActivityRecord) -> None:
        self._records.append(record)

    @t.override
    async def _find(self, query: AuthActivityQuery) -> tuple[AuthActivityRecord, ...]:
        found = [
            record for record in reversed(self._records) if _matches(record, query)
        ]
        found.sort(key=lambda record: record.when, reverse=True)  # stable
        return tuple(found[: query.limit])


def _matches(record: AuthActivityRecord, query: AuthActivityQuery) -> bool:
    return (
        query.entity_type in (None, record.entity_type)
        and query.entity_id in (None, record.entity_id)
        and query.who in (None, record.who)
        and query.session_id in (None, record.session_id)
        and query.action in (None, record.action)
        and (query.since is None or record.when >= query.since)
        and (query.until is None or record.when < query.until)
    )
