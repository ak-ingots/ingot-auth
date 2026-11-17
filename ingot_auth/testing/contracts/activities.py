"""The contract of the storage of the activity log."""

__all__ = ("AuthActivitiesStorageContract", "create_record")

import dataclasses
import datetime
import decimal
import typing as t

from ingot_auth.storages import (
    AuthActivityAction,
    AuthActivityQuery,
    AuthActivityRecord,
)

from .base import BaseAuthContract
from .profiles import NOW

HOUR: t.Final = datetime.timedelta(hours=1)


def create_record(**changes: t.Any) -> AuthActivityRecord:
    """A record of a tag created by root, its context one of each kind of value."""
    record = AuthActivityRecord(
        who="root",
        session_uid=None,
        action=AuthActivityAction.CREATE,
        entity_type="auth.profiles.tags",
        entity_uid="1",
        context={},
        run_uid="r1",
        when=NOW,
    )
    return dataclasses.replace(record, **changes)


class AuthActivitiesStorageContract(BaseAuthContract):
    """
    The activity log of a storage: a record found as appended, its context
    as kept; found by each filter, the newest first, as many as the limit.
    """

    async def test_a_record_is_found_as_appended(self) -> None:
        activities = self.project.auth.storage.activities
        context = {
            "flag": True,
            "count": 7,
            "price": decimal.Decimal("1.50"),
            "at": NOW,
            "name": "beta",
            "ids": [1, 3],
            "nested": {"kind": "email"},
        }
        record = create_record(session_uid="s1", context=context)
        await activities.append(record)
        self.assertEqual(await activities.find(AuthActivityQuery()), (record,))

    async def test_the_records_are_found_by_their_filters(self) -> None:
        activities = self.project.auth.storage.activities
        first = create_record()
        second = create_record(
            who="a1",
            session_uid="s1",
            action=AuthActivityAction.UPDATE,
            entity_type="auth.profiles",
            entity_uid="a1",
            when=NOW + HOUR,
        )
        third = create_record(entity_uid="2", when=NOW + 2 * HOUR)
        for record in (first, second, third):
            await activities.append(record)
        for query, found in (
            (AuthActivityQuery(), (third, second, first)),
            (AuthActivityQuery(limit=2), (third, second)),
            (AuthActivityQuery(entity_type="auth.profiles.tags"), (third, first)),
            (
                AuthActivityQuery(entity_type="auth.profiles.tags", entity_uid="1"),
                (first,),
            ),
            (AuthActivityQuery(who="a1"), (second,)),
            (AuthActivityQuery(session_uid="s1"), (second,)),
            (AuthActivityQuery(action=AuthActivityAction.CREATE), (third, first)),
            (AuthActivityQuery(since=NOW + HOUR), (third, second)),
            (AuthActivityQuery(until=NOW + HOUR), (first,)),
            (AuthActivityQuery(who="nobody"), ()),
        ):
            with self.subTest(query=query):
                self.assertEqual(await activities.find(query), found)
