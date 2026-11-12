import datetime
import hashlib
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import ROOT_CALLER, PermissionFlags, Permissions
from ingots.puer import Slot

from ingot_auth import AuthProject
from ingot_auth.__main__ import (
    AuthMemoryProject,
    AuthMemorySignInUnit,
    AuthMemoryUnit,
)
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import AuthGroup, AuthGroupsUnit
from ingot_auth.auth import AuthUnit
from ingot_auth.caches import AuthCaller
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.sessions import (
    AuthFixedLifetime,
    AuthSessionExpiredError,
    AuthSessionsUnit,
    AuthSlidingFixedLifetime,
    AuthSlidingLifetime,
    BaseAuthSessionLifetime,
)
from ingot_auth.storages import (
    AuthMembership,
    AuthProfile,
    AuthSessionCloseReason,
    AuthSessionNotFoundError,
)

DAY: t.Final = datetime.timedelta(days=1)
MINUTE: t.Final = datetime.timedelta(minutes=1)
NOW: t.Final = datetime.datetime(2026, 11, 12, tzinfo=datetime.UTC)


class ShopPermissions(PermissionFlags, domain="shop"):
    CAN_BUY = 1 << 0


class BuyersGroup(AuthGroup):
    @t.override
    def _get_permissions(self) -> Permissions:
        return super()._get_permissions() | Permissions(ShopPermissions.CAN_BUY)


class ShopGroupsUnit(AuthGroupsUnit):
    buyers = Slot(BuyersGroup)


class ShopAccessUnit(AuthAccessUnit):
    groups = Slot(ShopGroupsUnit)


class ShopAuthUnit(AuthMemoryUnit):
    access = Slot(ShopAccessUnit)


class ShopProject(AuthMemoryProject):
    auth = Slot(ShopAuthUnit)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class SessionsTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = ShopProject()
        self.sessions = self.project.auth.sessions
        await self.project.auth.storage.access.members.add(
            AuthMembership(group="buyers", uid="a1")
        )

    async def run_operation(self, factory: t.Any, parameters: t.Any) -> t.Any:
        """Runs an operation as the root."""
        operations = self.project.operations
        metadata = operations.create_metadata(ROOT_CALLER)
        return await operations.runner.run(factory, parameters, metadata)

    def travel(self, delta: datetime.timedelta) -> None:
        """Makes the sessions and their caches see a time that far ahead."""
        later = datetime.datetime.now(datetime.UTC) + delta
        cache = self.project.auth.cache
        for owner in (self.sessions, cache.sessions, cache.callers):
            self.enterContext(
                mock.patch.object(type(owner), "_get_now", return_value=later)
            )

    async def test_a_token_gives_the_caller_of_its_session(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {1: "iPhone"})
        caller = await self.sessions.authenticate(opened.token)
        session = await self.project.auth.storage.sessions.find(
            hash_token(opened.token)
        )
        self.assertEqual(session.id, opened.session_id)
        self.assertEqual(
            caller,
            AuthCaller(
                uid="a1",
                session_id=session.id,
                permissions=Permissions(ShopPermissions.CAN_BUY),
            ),
        )
        self.assertEqual(
            (session.uid, session.method, session.attr_values),
            ("a1", "nickname", {1: "iPhone"}),
        )

    async def test_the_token_is_random_and_kept_by_its_hash_alone(self) -> None:
        opened = await self.sessions.open("a1", "nickname", {})
        first = opened.token
        second = (await self.sessions.open("a1", "nickname", {})).token
        self.assertNotEqual(first, second)
        self.assertEqual(len(first), 43)  # 256 bits in base64
        session = await self.project.auth.storage.sessions.find(hash_token(first))
        self.assertNotIn(first, repr(session))
        self.assertNotIn(first, repr(opened))

    async def test_an_unknown_token_is_not_found_and_not_told(self) -> None:
        await self.sessions.open("a1", "nickname", {})
        with self.assertRaises(AuthSessionNotFoundError) as error:
            await self.sessions.authenticate("unknown")
        self.assertNotIn("unknown", str(error.exception))

    async def test_a_session_past_its_lifetime_expires_and_closes(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        await self.sessions.authenticate(token)
        self.travel(31 * DAY)
        with self.assertRaises(AuthSessionExpiredError) as error:
            await self.sessions.authenticate(token)
        self.assertEqual(
            error.exception.reason, AuthSessionCloseReason.EXPIRED_ABSOLUTE
        )
        with self.assertRaises(AuthSessionNotFoundError):
            await self.project.auth.storage.sessions.find(hash_token(token))
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(token)

    async def test_a_session_closed_meanwhile_expires_all_the_same(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        self.travel(31 * DAY)
        storage = type(self.project.auth.storage.sessions)
        closed = AuthSessionNotFoundError.for_id("s1")
        with mock.patch.object(storage, "_close", side_effect=closed):
            with self.assertRaises(AuthSessionExpiredError):
                await self.sessions.authenticate(token)

    async def test_a_cached_session_past_its_lifetime_is_found_again(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        caller = await self.sessions.authenticate(token)
        now = datetime.datetime.now(datetime.UTC)
        await self.project.auth.storage.sessions.close(
            caller.session_id, AuthSessionCloseReason.SIGNED_OUT, now
        )
        expired = AuthSessionCloseReason.EXPIRED_ABSOLUTE
        lifetime = type(self.sessions.lifetime)
        with mock.patch.object(lifetime, "_expire", return_value=expired):
            with self.assertRaises(AuthSessionNotFoundError):
                await self.sessions.authenticate(token)
        # closed by another, so forgotten in the cache
        self.assertIsNone(await self.project.auth.cache.sessions.get(hash_token(token)))

    async def test_a_cached_request_reads_nothing_from_the_storage(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        caller = await self.sessions.authenticate(token)
        storage = self.project.auth.storage
        with (
            mock.patch.object(type(storage.sessions), "_find", side_effect=OSError),
            mock.patch.object(
                type(storage.access.members), "_get_groups", side_effect=OSError
            ),
        ):
            self.assertEqual(await self.sessions.authenticate(token), caller)

    async def test_a_caller_is_formed_again_past_the_ttl_of_the_cache(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        await self.sessions.authenticate(token)
        await self.project.auth.storage.access.members.remove(
            AuthMembership(group="buyers", uid="a1")
        )
        buyer = Permissions(ShopPermissions.CAN_BUY)
        self.assertEqual((await self.sessions.authenticate(token)).permissions, buyer)
        self.travel(datetime.timedelta(minutes=6))
        self.assertEqual(
            (await self.sessions.authenticate(token)).permissions, Permissions()
        )

    async def test_a_change_of_the_groups_of_a_user_shows_on_its_next_request(
        self,
    ) -> None:
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        storage = self.project.auth.storage
        for uid in ("a1", "b2"):
            await storage.profiles.create(AuthProfile(uid=uid, created_at=NOW))
        await storage.access.members.add(AuthMembership(group="buyers", uid="b2"))
        tokens = [
            (await self.sessions.open(uid, "nickname", {})).token
            for uid in ("a1", "a1", "b2")
        ]
        for token in tokens:
            await self.sessions.authenticate(token)
        members = self.project.auth.access.members
        membership = AuthMembership(group="buyers", uid="a1")
        buyer = Permissions(ShopPermissions.CAN_BUY)
        for factory, permissions in (
            (members.op_remove, Permissions()),
            (members.op_add, buyer),
        ):
            await self.run_operation(factory, membership)
            for token in tokens[:2]:
                caller = await self.sessions.authenticate(token)
                self.assertEqual(caller.permissions, permissions)
            # the other user is not forgotten, its sessions are kept
            with mock.patch.object(
                type(storage.access.members), "_get_groups", side_effect=OSError
            ):
                caller = await self.sessions.authenticate(tokens[2])
            self.assertEqual(caller.permissions, buyer)
        self.assertEqual(len(await storage.sessions.get_open("a1")), 2)

    async def test_a_caller_formed_by_other_groups_is_formed_again(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        await self.sessions.authenticate(token)
        await self.project.auth.storage.access.members.remove(
            AuthMembership(group="buyers", uid="a1")
        )
        groups = self.project.auth.access.groups
        with mock.patch.object(type(groups), "get_digest", return_value="deployed"):
            caller = await self.sessions.authenticate(token)
        self.assertEqual(caller.permissions, Permissions())

    async def test_a_session_closed_in_the_storage_ends_past_the_cache(self) -> None:
        token = (await self.sessions.open("a1", "nickname", {})).token
        caller = await self.sessions.authenticate(token)
        await self.project.auth.storage.sessions.close(
            caller.session_id,
            AuthSessionCloseReason.REVOKED,
            datetime.datetime.now(datetime.UTC),
        )
        self.travel(datetime.timedelta(minutes=6))
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(token)


class SlidingSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthSlidingLifetime)


class SlidingAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(SlidingSessionsUnit)
    sign_in = Slot(AuthMemorySignInUnit)


class SlidingProject(AuthProject):
    auth = Slot(SlidingAuthUnit)


class SlidingFixedSessionsUnit(SlidingSessionsUnit):
    lifetime = Slot(AuthSlidingFixedLifetime)


class SlidingFixedAuthUnit(SlidingAuthUnit):
    sessions = Slot(SlidingFixedSessionsUnit)


class SlidingFixedProject(SlidingProject):
    auth = Slot(SlidingFixedAuthUnit)


class SlidingTestCase(unittest.IsolatedAsyncioTestCase):
    project: SlidingProject

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.use(SlidingProject())
        self.opened_at = datetime.datetime.now(datetime.UTC)

    def use(self, project: SlidingProject) -> None:
        """Runs the test on a project of a lifetime of its own."""
        self.project = project
        self.sessions = project.auth.sessions
        self.storage = project.auth.storage.sessions

    def travel(self, delta: datetime.timedelta) -> None:
        """Makes the sessions and their caches see that long after the sign-in."""
        later = self.opened_at + delta
        cache = self.project.auth.cache
        for owner in (self.sessions, cache.sessions, cache.callers):
            self.enterContext(
                mock.patch.object(type(owner), "_get_now", return_value=later)
            )

    async def open(self) -> str:
        """Opens a session at the time of the test, giving its token."""
        self.travel(datetime.timedelta())
        return (await self.sessions.open("a1", "nickname", {})).token

    async def get_seen_at(self, token: str) -> datetime.timedelta:
        """How long after the sign-in the storage has the session seen."""
        session = await self.storage.find(hash_token(token))
        return session.seen_at - self.opened_at

    async def test_a_session_used_lives_on(self) -> None:
        token = await self.open()
        for minutes in (50, 100, 150):
            self.travel(minutes * MINUTE)
            await self.sessions.authenticate(token)
            self.assertEqual(await self.get_seen_at(token), minutes * MINUTE)

    async def test_a_session_idle_expires(self) -> None:
        token = await self.open()
        self.travel(50 * MINUTE)
        await self.sessions.authenticate(token)
        self.travel(110 * MINUTE)
        with self.assertRaises(AuthSessionExpiredError) as error:
            await self.sessions.authenticate(token)
        self.assertEqual(error.exception.reason, AuthSessionCloseReason.EXPIRED_IDLE)
        with self.assertRaises(AuthSessionNotFoundError):
            await self.storage.find(hash_token(token))

    async def test_the_time_seen_is_written_once_an_interval(self) -> None:
        token = await self.open()
        for minutes, seen in ((3, 0), (6, 6), (9, 6), (12, 12)):
            self.travel(minutes * MINUTE)
            await self.sessions.authenticate(token)
            self.assertEqual(await self.get_seen_at(token), seen * MINUTE)
            # the cache has it too, not to write it again on the next request
            cached = await self.project.auth.cache.sessions.get(hash_token(token))
            assert cached is not None
            self.assertEqual(cached.seen_at - self.opened_at, seen * MINUTE)

    async def test_a_cached_session_seen_by_another_lives(self) -> None:
        self.project.settings.configs.apply({"AUTH_SESSION_CACHE_TTL": 86400})
        token = await self.open()
        caller = await self.sessions.authenticate(token)
        # another process saw it, its cache not this one
        await self.storage.touch(caller.session_id, self.opened_at + 50 * MINUTE)
        self.travel(70 * MINUTE)
        self.assertEqual(await self.sessions.authenticate(token), caller)

    async def test_a_session_closed_meanwhile_is_not_seen(self) -> None:
        self.project.settings.configs.apply({"AUTH_SESSION_CACHE_TTL": 86400})
        token = await self.open()
        caller = await self.sessions.authenticate(token)
        await self.storage.close(
            caller.session_id, AuthSessionCloseReason.REVOKED, self.opened_at
        )
        self.travel(10 * MINUTE)
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(token)
        self.assertIsNone(await self.project.auth.cache.sessions.get(hash_token(token)))

    async def test_both_expire_by_whichever_comes_first(self) -> None:
        self.use(SlidingFixedProject())
        self.project.settings.configs.apply({"AUTH_SESSION_TTL": 3 * 3600})
        idle, used = await self.open(), await self.open()
        expired = []
        steps = ((50, used), (70, idle), (100, used), (150, used), (180, used))
        for minutes, token in steps:
            self.travel(minutes * MINUTE)
            try:
                await self.sessions.authenticate(token)
            except AuthSessionExpiredError as error:
                expired.append((minutes, error.reason))
        self.assertEqual(
            expired,
            [
                (70, AuthSessionCloseReason.EXPIRED_IDLE),
                (180, AuthSessionCloseReason.EXPIRED_ABSOLUTE),
            ],
        )


class LifetimeTestCase(unittest.TestCase):
    def test_the_sessions_have_no_lifetime_by_default(self) -> None:
        self.assertIs(AuthSessionsUnit.lifetime.cls, BaseAuthSessionLifetime)

    def test_a_fixed_lifetime_lasts_its_ttl_from_the_sign_in(self) -> None:
        project = AuthMemoryProject()
        lifetime = project.auth.sessions.lifetime
        self.assertIsInstance(lifetime, AuthFixedLifetime)
        opened_at = datetime.datetime(2026, 11, 10, tzinfo=datetime.UTC)
        session = mock.Mock(opened_at=opened_at)
        self.assertIsNone(lifetime.check(session, opened_at + 30 * DAY - DAY / 24))
        self.assertEqual(
            lifetime.check(session, opened_at + 30 * DAY),
            AuthSessionCloseReason.EXPIRED_ABSOLUTE,
        )
