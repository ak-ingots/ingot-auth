import contextlib
import datetime
import io
import os
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, OperationPermissionsError
from ingots.puer import Slot
from ingots.defaults.cli import CommandRunner

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.contrib.storages.memory.sessions import AuthMemorySessionsStorage
from ingot_auth.activities import AuthListActivitiesParameters
from ingot_auth.sessions import AuthListSessionsParameters
from ingot_auth.storages import (
    AuthMembership,
    AuthSessionCloseReason,
    AuthSessionRecord,
)
from tests import QUIET, ROOT

NOW = datetime.datetime(2026, 11, 15, 12, tzinfo=datetime.UTC)


class RecordTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = AuthMemoryProject()
        self.sessions = self.project.auth.sessions
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="auth.sessions.grp_admins", profile_uid="op")
        )

    async def run_operation(
        self, factory: t.Any, parameters: t.Any, caller: Caller
    ) -> t.Any:
        operations = self.project.operations
        metadata = operations.create_metadata(caller)
        return await operations.runner.run(factory, parameters, metadata)

    async def caller_of(self, uid: str) -> Caller:
        opened = await self.sessions.open(uid, "nickname", {})
        return await self.sessions.authenticate(opened.token)

    async def test_the_record_tells_when_and_why_the_log_who(self) -> None:
        phone = await self.sessions.open("a1", "nickname", {1: "phone"})
        tablet = await self.sessions.open("a1", "nickname", {1: "tablet"})
        user = await self.caller_of("a1")
        await self.run_operation(self.sessions.op_revoke_others, None, user)
        await self.run_operation(self.project.auth.sign_out.op_sign_out, None, user)
        kept = await self.sessions.open("a1", "nickname", {})
        operator = await self.caller_of("op")
        record = await self.run_operation(
            self.sessions.op_list,
            AuthListSessionsParameters(profile_uid="a1", closed=True),
            operator,
        )
        self.assertEqual(
            [(s.uid, s.close_reason) for s in record],
            [
                (phone.session_uid, AuthSessionCloseReason.REVOKED),
                (tablet.session_uid, AuthSessionCloseReason.REVOKED),
                (record[2].uid, AuthSessionCloseReason.SIGNED_OUT),
                (kept.session_uid, None),
            ],
        )
        self.assertEqual(record[0].attr_values, {1: "phone"})
        self.assertNotIn(phone.token, repr(record))
        log = self.project.auth.storage.activities
        for session in record[:3]:
            query = AuthListActivitiesParameters(
                entity_type="auth.sessions", entity_uid=session.uid
            )
            (closed,) = await log.find(query)
            self.assertEqual(closed.who, "a1")
        open_only = await self.run_operation(
            self.sessions.op_list,
            AuthListSessionsParameters(profile_uid="a1"),
            operator,
        )
        self.assertEqual([s.uid for s in open_only], [kept.session_uid])

    async def test_an_expired_session_is_closed_by_the_server(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=31)
        with mock.patch.object(type(self.sessions), "_get_now", return_value=later):
            with contextlib.suppress(Exception):
                await self.sessions.authenticate(opened.token)
        record = await self.run_operation(
            self.sessions.op_list,
            AuthListSessionsParameters(profile_uid="a1", closed=True),
            ROOT,
        )
        self.assertEqual(
            record[0].close_reason, AuthSessionCloseReason.EXPIRED_ABSOLUTE
        )
        query = AuthListActivitiesParameters(entity_uid=opened.session_uid)
        (expired,) = await self.project.auth.storage.activities.find(query)
        self.assertEqual(expired.who, "auth.system")

    async def test_the_user_may_not_read_the_record(self) -> None:
        user = await self.caller_of("a1")
        with self.assertRaises(OperationPermissionsError):
            await self.run_operation(
                self.sessions.op_list,
                AuthListSessionsParameters(profile_uid="a1"),
                user,
            )


class SeededSessionsStorage(AuthMemorySessionsStorage):
    def __init__(self) -> None:
        super().__init__()
        later = NOW + datetime.timedelta(hours=1)
        for record in (
            AuthSessionRecord(
                uid="s1",
                profile_uid="a1",
                method="nickname",
                token_hash="h1",
                attr_values={2: "PL", 1: "iPhone"},
                opened_at=NOW,
                seen_at=NOW,
                closed_at=later,
                close_reason=AuthSessionCloseReason.REVOKED,
            ),
            AuthSessionRecord(
                uid="s2",
                profile_uid="a1",
                method="email_code",
                token_hash="h2",
                attr_values={},
                opened_at=later,
                seen_at=later,
                closed_at=later,
                close_reason=AuthSessionCloseReason.EXPIRED_IDLE,
            ),
            AuthSessionRecord(
                uid="s3",
                profile_uid="a1",
                method="nickname",
                token_hash="h3",
                attr_values={},
                opened_at=later,
                seen_at=later,
            ),
        ):
            self._sessions[record.uid] = record


class SeededStorage(AuthMemoryStorage):
    sessions = Slot(SeededSessionsStorage)


class SeededAuthUnit(AuthMemoryUnit):
    storage = Slot(SeededStorage)


class SeededProject(AuthMemoryProject):
    auth = Slot(SeededAuthUnit)


class CommandsTestCase(unittest.TestCase):
    @t.override
    def setUp(self) -> None:
        self.enterContext(mock.patch.dict(os.environ, clear=True))

    def run_project(self, *argv: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = CommandRunner(SeededProject, [*QUIET, *argv]).run()
        return code, out.getvalue()

    def test_the_record_of_a_profile_is_printed(self) -> None:
        self.assertEqual(
            self.run_project("auth", "sessions", "list", "a1", "--closed"),
            (
                0,
                "s1\tnickname\t2026-11-15T12:00:00+00:00\t2026-11-15T12:00:00+00:00"
                "\t2026-11-15T13:00:00+00:00\trevoked\t1=iPhone\t2=PL\n"
                "s2\temail_code\t2026-11-15T13:00:00+00:00\t2026-11-15T13:00:00+00:00"
                "\t2026-11-15T13:00:00+00:00\texpired_idle\n"
                "s3\tnickname\t2026-11-15T13:00:00+00:00\t2026-11-15T13:00:00+00:00\n",
            ),
        )
        self.assertEqual(
            self.run_project("auth", "sessions", "list", "a1"),
            (0, "s3\tnickname\t2026-11-15T13:00:00+00:00\t2026-11-15T13:00:00+00:00\n"),
        )
