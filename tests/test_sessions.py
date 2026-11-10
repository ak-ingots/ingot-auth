import datetime
import hashlib
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import PermissionFlags, Permissions
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import AuthGroup, AuthGroupsUnit
from ingot_auth.access.members import AuthMembership
from ingot_auth.sessions import (
    AuthCaller,
    AuthFixedLifetime,
    AuthSessionCloseReason,
    AuthSessionExpiredError,
    AuthSessionNotFoundError,
    AuthSessionsUnit,
    BaseAuthSessionLifetime,
)

DAY: t.Final = datetime.timedelta(days=1)


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

    def travel(self, delta: datetime.timedelta) -> None:
        """Makes the sessions and their caches see a time that far ahead."""
        later = datetime.datetime.now(datetime.UTC) + delta
        cache = self.project.auth.cache
        for owner in (self.sessions, cache.sessions, cache.callers):
            self.enterContext(
                mock.patch.object(type(owner), "_get_now", return_value=later)
            )

    async def test_a_token_gives_the_caller_of_its_session(self) -> None:
        token = await self.sessions.open("a1", "nickname", {1: "iPhone"})
        caller = await self.sessions.authenticate(token)
        session = await self.project.auth.storage.sessions.find(hash_token(token))
        self.assertEqual(
            caller,
            AuthCaller(
                uid="a1",
                session_id=session.id,
                permissions=Permissions(ShopPermissions.CAN_BUY),
            ),
        )
        self.assertEqual(
            (session.uid, session.method, session.values),
            ("a1", "nickname", {1: "iPhone"}),
        )

    async def test_the_token_is_random_and_kept_by_its_hash_alone(self) -> None:
        first = await self.sessions.open("a1", "nickname", {})
        second = await self.sessions.open("a1", "nickname", {})
        self.assertNotEqual(first, second)
        self.assertEqual(len(first), 43)  # 256 bits in base64
        session = await self.project.auth.storage.sessions.find(hash_token(first))
        self.assertNotIn(first, repr(session))

    async def test_an_unknown_token_is_not_found_and_not_told(self) -> None:
        await self.sessions.open("a1", "nickname", {})
        with self.assertRaises(AuthSessionNotFoundError) as error:
            await self.sessions.authenticate("unknown")
        self.assertNotIn("unknown", str(error.exception))

    async def test_a_session_past_its_lifetime_expires_and_closes(self) -> None:
        token = await self.sessions.open("a1", "nickname", {})
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
        token = await self.sessions.open("a1", "nickname", {})
        caller = await self.sessions.authenticate(token)
        now = datetime.datetime.now(datetime.UTC)
        await self.project.auth.storage.sessions.close(
            caller.session_id, AuthSessionCloseReason.SIGNED_OUT, now
        )
        expired = AuthSessionCloseReason.EXPIRED_ABSOLUTE
        lifetime = type(self.sessions.lifetime)
        with mock.patch.object(lifetime, "_expire", return_value=expired):
            with self.assertRaises(AuthSessionExpiredError):
                await self.sessions.authenticate(token)

    async def test_a_cached_request_reads_nothing_from_the_storage(self) -> None:
        token = await self.sessions.open("a1", "nickname", {})
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
        token = await self.sessions.open("a1", "nickname", {})
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

    async def test_a_session_closed_in_the_storage_ends_past_the_cache(self) -> None:
        token = await self.sessions.open("a1", "nickname", {})
        caller = await self.sessions.authenticate(token)
        await self.project.auth.storage.sessions.close(
            caller.session_id,
            AuthSessionCloseReason.REVOKED,
            datetime.datetime.now(datetime.UTC),
        )
        self.travel(datetime.timedelta(minutes=6))
        with self.assertRaises(AuthSessionNotFoundError):
            await self.sessions.authenticate(token)


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
