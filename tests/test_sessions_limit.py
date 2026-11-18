import datetime
import typing as t
from unittest import mock

from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemorySignInUnit
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.activities import AuthListActivitiesParameters
from ingot_auth.project import AuthProject
from ingot_auth.sessions import (
    AuthFixedLifetime,
    AuthNoLimit,
    AuthNoSessionAttrsDeriver,
    AuthRefuseLimit,
    AuthSessionsLimitError,
    AuthSessionsUnit,
)
from ingot_auth.sign_in import AuthSignedIn
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionNotFoundError
from ingot_auth.testing.methods import AuthTestingStart

from tests.test_sign_in import BaseSignInTestCase, TstMethodsUnit


class LimitedSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)
    deriver = Slot(AuthNoSessionAttrsDeriver)


class RefusingSessionsUnit(LimitedSessionsUnit):
    limit = Slot(AuthRefuseLimit)


class FreeSessionsUnit(LimitedSessionsUnit):
    limit = Slot(AuthNoLimit)


class LimitedAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(LimitedSessionsUnit)
    methods = Slot(TstMethodsUnit)
    sign_in = Slot(AuthMemorySignInUnit)


class RefusingAuthUnit(LimitedAuthUnit):
    sessions = Slot(RefusingSessionsUnit)


class FreeAuthUnit(LimitedAuthUnit):
    sessions = Slot(FreeSessionsUnit)


class RefusingProject(AuthProject):
    auth = Slot(RefusingAuthUnit)


class FreeProject(AuthProject):
    auth = Slot(FreeAuthUnit)


class BaseLimitTestCase(BaseSignInTestCase):
    """A profile signing in again and again, ``AUTH_SESSIONS_MAX`` of its own."""

    MAX: t.ClassVar = 2

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.limit_to(self.MAX)
        self.uid = await self.sign_up("a@b.c")
        self.now = datetime.datetime.now(datetime.UTC)
        self.enterContext(
            mock.patch.object(
                AuthSessionsUnit, "_get_now", side_effect=lambda: self.now
            )
        )

    def limit_to(self, count: int) -> None:
        """``AUTH_SESSIONS_MAX``, as the operator restarting the server sets it."""
        configs = self.project.settings.configs
        values = {"AUTH_SESSIONS_MAX": count}
        self.enterContext(mock.patch.object(configs, "_configs_values", values))

    async def sign_in(self) -> AuthSignedIn:
        result = await self.start(AuthTestingStart(subject="a@b.c"))
        assert isinstance(result, AuthSignedIn)
        self.travel(seconds=1)  # the next one opens later
        return result

    def travel(self, **delta: float) -> None:
        self.now += datetime.timedelta(**delta)

    async def get_reasons(self) -> list[AuthSessionCloseReason | None]:
        """The reason each session of the profile closed for, by its opening."""
        sessions = await self.project.auth.storage.sessions.get_all(self.uid)
        return [session.close_reason for session in sessions]

    async def get_actions(self) -> list[tuple[str, str]]:
        """The actions of the log on the sessions, each with its run."""
        records = await self.project.auth.storage.activities.find(
            AuthListActivitiesParameters()
        )
        return [
            (record.action, record.run_uid)
            for record in reversed(records)  # the newest first
            if record.entity_type == "auth.sessions"
        ]


class EvictOldestTestCase(BaseLimitTestCase):
    async def test_a_sign_in_over_the_limit_evicts_the_one_seen_longest_ago(
        self,
    ) -> None:
        first = await self.sign_in()
        self.travel(minutes=1)
        second = await self.sign_in()
        self.travel(minutes=10)
        # seen: the fixed lifetime writes no time seen, a sliding one would
        await self.project.auth.storage.sessions.touch(first.session_uid, self.now)
        self.travel(minutes=1)
        await self.sign_in()
        self.assertEqual(
            await self.get_reasons(), [None, AuthSessionCloseReason.EVICTED, None]
        )
        with self.assertRaises(AuthSessionNotFoundError):  # forgotten
            await self.project.auth.sessions.authenticate(second.token)
        await self.project.auth.sessions.authenticate(first.token)

    async def test_the_eviction_is_logged_in_the_run_of_the_sign_in(self) -> None:
        for _ in range(3):
            await self.sign_in()
        actions = await self.get_actions()
        self.assertEqual(
            [action for action, _ in actions],
            ["sign_in", "sign_in", "evict", "sign_in"],
        )
        self.assertEqual(actions[2][1], actions[3][1])

    async def test_a_limit_of_one_signs_out_the_earlier_sign_in(self) -> None:
        self.limit_to(1)
        await self.sign_in()
        await self.sign_in()
        self.assertEqual(
            await self.get_reasons(), [AuthSessionCloseReason.EVICTED, None]
        )

    async def test_a_limit_below_one_keeps_the_session_it_opens(self) -> None:
        self.limit_to(0)
        await self.sign_in()
        await self.sign_in()
        self.assertEqual(
            await self.get_reasons(), [AuthSessionCloseReason.EVICTED, None]
        )

    async def test_a_lower_limit_evicts_down_to_it_at_the_next_sign_in(self) -> None:
        self.limit_to(4)
        for _ in range(4):
            await self.sign_in()
        self.limit_to(2)
        await self.sign_in()
        self.assertEqual((await self.get_reasons()).count(None), 2)

    async def test_an_expired_session_takes_no_room_and_is_left_open(
        self,
    ) -> None:
        await self.sign_in()
        self.travel(days=29)
        await self.sign_in()
        self.travel(days=2)  # the first one past its fixed lifetime of 30
        await self.sign_in()
        # closed by its request or the sweep, not by a sign-in
        self.assertEqual(await self.get_reasons(), [None, None, None])
        self.assertNotIn("expire", [a for a, _ in await self.get_actions()])

    async def test_a_session_closed_meanwhile_is_skipped(self) -> None:
        for _ in range(2):
            await self.sign_in()
        storage = self.project.auth.storage.sessions
        open_ = await storage.get_open(self.uid)
        get_open = mock.AsyncMock(return_value=open_)
        await storage.close(open_[0].uid, AuthSessionCloseReason.REVOKED, self.now)
        with mock.patch.object(type(storage), "get_open", get_open):
            await self.sign_in()
        self.assertEqual(
            await self.get_reasons(), [AuthSessionCloseReason.REVOKED, None, None]
        )


class RefuseTestCase(BaseLimitTestCase):
    @t.override
    def create_project(self) -> AuthProject:
        return RefusingProject()

    async def test_a_sign_in_over_the_limit_is_refused_keeping_nothing(self) -> None:
        await self.sign_in()
        await self.sign_in()
        with self.assertRaises(AuthSessionsLimitError) as caught:
            await self.sign_in()
        self.assertEqual(caught.exception.count, 2)
        self.assertEqual(str(caught.exception), "as many open sessions as allowed: 2")
        self.assertEqual(await self.get_reasons(), [None, None])
        self.assertEqual(
            [action for action, _ in await self.get_actions()], ["sign_in", "sign_in"]
        )


class NoLimitTestCase(BaseLimitTestCase):
    @t.override
    def create_project(self) -> AuthProject:
        return FreeProject()

    async def test_any_number_of_sessions_stays_open(self) -> None:
        for _ in range(4):
            await self.sign_in()
        self.assertEqual(await self.get_reasons(), [None] * 4)

    async def test_a_sign_in_reads_no_session(self) -> None:
        await self.sign_in()
        self.travel(days=31)  # expired: closed by its request or the sweep
        get_open = mock.AsyncMock()
        storage = self.project.auth.storage.sessions
        with mock.patch.object(type(storage), "get_open", get_open):
            await self.sign_in()
        get_open.assert_not_called()
        self.assertEqual(await self.get_reasons(), [None, None])
