import asyncio
import contextlib
import dataclasses
import hashlib
import typing as t
import unittest
from collections.abc import Mapping
from unittest import mock

from ingots.defaults.operations import (
    Caller,
    OperationPermissionsError,
    Permissions,
)
from ingots.puer import Slot

from ingot_auth.__main__ import (
    AuthMemoryProject,
    AuthMemorySessionsUnit,
    AuthMemorySignInUnit,
    AuthMemoryUnit,
)
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.project import AuthProject
from ingot_auth.access.groups import AuthSignedInGroup
from ingot_auth.caches import AuthAttemptNotFoundError
from ingot_auth.methods import (
    AuthMethodDeniedError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
)
from ingot_auth.sessions import (
    AuthEvictOldestLimit,
    AuthFixedLifetime,
    AuthSessionsUnit,
    BaseAuthSessionAttrsDeriver,
)
from ingot_auth.sign_in import (
    AuthAnswerSignInParameters,
    AuthFloorTiming,
    AuthNoTiming,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInUnit,
    AuthSignInResult,
    AuthStartSignInParameters,
    BaseAuthTiming,
)
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthStartSignUpParameters,
)
from ingot_auth.storages import (
    AuthAttrType,
    AuthAttrValue,
    AuthSessionAttr,
    AuthSessionAttrSource,
)
from ingot_auth.testing.methods import (
    AuthTestingMethod,
    AuthTestingStart,
)

from tests import OWN, masks


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class TstMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class FloorSignInUnit(AuthSignInUnit):
    timing = Slot(AuthFloorTiming)


# the timing of the unit in memory is none, which no floor extends: an auth
# in memory of its own, with a floor
class FloorAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(AuthMemorySessionsUnit)
    methods = Slot(TstMethodsUnit)
    sign_in = Slot(FloorSignInUnit)


class FloorProject(AuthProject):
    auth = Slot(FloorAuthUnit)


class ClosedSignedInGroup(AuthSignedInGroup):
    """Takes the sign-in of every method off the profiles."""

    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()


class ClosedAuthUnit(TstAuthUnit):
    grp_signed_in = Slot(ClosedSignedInGroup)


class ClosedProject(AuthMemoryProject):
    auth = Slot(ClosedAuthUnit)


class CountryDeriver(BaseAuthSessionAttrsDeriver):
    """The country of an IP, as a base of GeoIP tells it, and wrong values."""

    @t.override
    async def _derive(
        self, attr_values: "Mapping[str, AuthAttrValue]"
    ) -> "Mapping[str, AuthAttrValue]":
        if attr_values.get("ip") != "192.0.2.1":
            return {}
        return {"country": "PL", "device": "derived", "city": 7, "unknown": 1}


class DerivingSessionsUnit(AuthSessionsUnit):
    lifetime = Slot(AuthFixedLifetime)
    deriver = Slot(CountryDeriver)
    limit = Slot(AuthEvictOldestLimit)


class DerivingAuthUnit(AuthUnit):
    storage = Slot(AuthMemoryStorage)
    cache = Slot(AuthMemoryCache)
    sessions = Slot(DerivingSessionsUnit)
    methods = Slot(TstMethodsUnit)
    sign_in = Slot(AuthMemorySignInUnit)


class DerivingProject(AuthProject):
    auth = Slot(DerivingAuthUnit)


class BaseSignInTestCase(unittest.IsolatedAsyncioTestCase):
    """The project of a test case and the calls of the sign-in, no test."""

    project: AuthProject

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = self.create_project()
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                uid=1,
                name="device",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.CLIENT,
            )
        )

    def create_project(self) -> AuthProject:
        return TstProject()

    def create_caller(self) -> Caller:
        """The anonymous caller of a server whose flows are open."""
        return self.project.operations.callers.get_anonymous()

    async def sign_up(self, subject: str) -> str:
        start = AuthStartSignUpParameters(
            method="testing", parameters=AuthTestingStart(subject=subject)
        )
        result = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start,
            start,
            self.project.operations.create_metadata(self.create_caller()),
        )
        assert isinstance(result, AuthSignedUp)
        return result.uid

    async def start(
        self,
        start: AuthTestingStart,
        caller: Caller | None = None,
        **attr_values: t.Any,
    ) -> AuthSignInResult:
        parameters = AuthStartSignInParameters(
            method="testing",
            parameters=start,
            attr_values={
                int(key.removeprefix("a")): value for key, value in attr_values.items()
            },
        )
        return await self.project.operations.runner.run(
            self.project.auth.sign_in.op_start,
            parameters,
            self.project.operations.create_metadata(caller or self.create_caller()),
        )

    async def answer(self, attempt_uid: str, answer: str) -> AuthSignInResult:
        parameters = AuthAnswerSignInParameters(attempt_uid=attempt_uid, answer=answer)
        return await self.project.operations.runner.run(
            self.project.auth.sign_in.op_answer,
            parameters,
            self.project.operations.create_metadata(self.create_caller()),
        )


class SignInTestCase(BaseSignInTestCase):
    async def test_a_profile_signs_in_and_its_token_gives_its_caller(self) -> None:
        uid = await self.sign_up("a@b.c")
        result = await self.start(AuthTestingStart(subject="a@b.c"), a1="iPhone")
        assert isinstance(result, AuthSignedIn)
        caller = await self.project.auth.sessions.authenticate(result.token)
        self.assertEqual((caller.uid, caller.session_uid), (uid, result.session_uid))
        self.assertEqual(
            caller.permissions, masks(AuthTestingMethod.Flags.CAN_SIGN_IN) | OWN
        )
        session = await self.project.auth.storage.sessions.find(
            hash_token(result.token)
        )
        self.assertEqual(
            (session.profile_uid, session.method, session.attr_values),
            (uid, "testing", {1: "iPhone"}),
        )
        self.assertNotIn(result.token, repr(result))

    async def test_the_session_keeps_the_values_of_the_transport(self) -> None:
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                uid=2,
                name="ip",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.TRANSPORT,
            )
        )
        await self.sign_up("a@b.c")
        parameters = AuthStartSignInParameters(
            method="testing",
            parameters=AuthTestingStart(subject="a@b.c"),
            attr_values={1: "iPhone"},
            transport_attr_values={"ip": "10.0.0.1"},
        )
        result = await self.project.operations.runner.run(
            self.project.auth.sign_in.op_start,
            parameters,
            self.project.operations.create_metadata(self.create_caller()),
        )
        assert isinstance(result, AuthSignedIn)
        session = await self.project.auth.storage.sessions.find(
            hash_token(result.token)
        )
        self.assertEqual(session.attr_values, {1: "iPhone", 2: "10.0.0.1"})

    async def test_a_method_of_two_steps_signs_in_by_the_answer(self) -> None:
        uid = await self.sign_up("a@b.c")
        challenge = await self.start(AuthTestingStart(subject="a@b.c", code="1"))
        assert isinstance(challenge, AuthSignInChallenge)
        self.assertEqual(challenge.challenge, "code")
        with self.assertRaises(AuthMethodRefusedError):
            await self.answer(challenge.attempt_uid, "2")
        result = await self.answer(challenge.attempt_uid, "1")
        assert isinstance(result, AuthSignedIn)
        caller = await self.project.auth.sessions.authenticate(result.token)
        self.assertEqual(caller.uid, uid)

    async def test_a_subject_bound_to_no_profile_is_refused(self) -> None:
        with self.assertRaises(AuthMethodRefusedError):
            await self.start(AuthTestingStart(subject="a@b.c"))

    async def test_an_attempt_of_a_sign_up_is_none_of_a_sign_in(self) -> None:
        start = AuthStartSignUpParameters(
            method="testing", parameters=AuthTestingStart(subject="a", code="1")
        )
        challenge = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start,
            start,
            self.project.operations.create_metadata(self.create_caller()),
        )
        assert isinstance(challenge, AuthSignUpChallenge)
        with self.assertRaises(AuthAttemptNotFoundError):
            await self.answer(challenge.attempt_uid, "1")

    def test_the_anonymous_caller_gets_the_flag_of_the_sign_in(self) -> None:
        self.assertEqual(
            self.project.auth.sign_in.get_anonymous_permissions(),
            masks(AuthSignInUnit.Flags.CAN_SIGN_IN),
        )

    async def test_signing_in_needs_the_flags_of_the_flow_and_the_method(
        self,
    ) -> None:
        await self.sign_up("a@b.c")
        sign_in = self.project.auth.sign_in
        for factory in (sign_in.op_start, sign_in.op_answer):
            self.assertEqual(
                factory().get_permissions(), masks(AuthSignInUnit.Flags.CAN_SIGN_IN)
            )
        caller = self.create_caller()
        for lacking in (
            AuthSignInUnit.Flags.CAN_SIGN_IN,
            AuthTestingMethod.Flags.CAN_SIGN_IN,
        ):
            with self.subTest(lacking=lacking):
                without = dataclasses.replace(
                    caller, permissions=caller.permissions - masks(lacking)
                )
                with self.assertRaises(OperationPermissionsError):
                    await self.start(AuthTestingStart(subject="a@b.c"), without)

    async def test_a_profile_without_the_sign_in_of_the_method_is_denied(
        self,
    ) -> None:
        self.project = ClosedProject()
        await self.sign_up("a@b.c")
        with self.assertRaises(AuthMethodDeniedError) as error:
            await self.start(AuthTestingStart(subject="a@b.c"))
        self.assertEqual(error.exception.name, "testing")
        self.assertEqual(
            str(error.exception), "the method 'testing' is closed to the profile"
        )


class DerivingTestCase(BaseSignInTestCase):
    @t.override
    def create_project(self) -> AuthProject:
        return DerivingProject()

    async def test_the_session_keeps_the_values_derived_from_the_others(
        self,
    ) -> None:
        attrs = self.project.auth.storage.sessions.attrs
        for attr_uid, name, source in (
            (2, "ip", AuthSessionAttrSource.TRANSPORT),
            (3, "country", AuthSessionAttrSource.DERIVED),
            (4, "city", AuthSessionAttrSource.DERIVED),
        ):
            await attrs.create(
                AuthSessionAttr(
                    uid=attr_uid, name=name, type=AuthAttrType.STR, source=source
                )
            )
        await self.sign_up("a@b.c")
        parameters = AuthStartSignInParameters(
            method="testing",
            parameters=AuthTestingStart(subject="a@b.c"),
            attr_values={1: "iPhone"},
            transport_attr_values={"ip": "192.0.2.1"},
        )
        with self.assertLogs("ingot_auth.sessions.attrs.values", "WARNING") as logs:
            result = await self.project.operations.runner.run(
                self.project.auth.sign_in.op_start,
                parameters,
                self.project.operations.create_metadata(self.create_caller()),
            )
        assert isinstance(result, AuthSignedIn)
        session = await self.project.auth.storage.sessions.find(
            hash_token(result.token)
        )
        # the device is of the client, the city a str: both dropped, warned
        self.assertEqual(session.attr_values, {1: "iPhone", 2: "192.0.2.1", 3: "PL"})
        self.assertEqual(len(logs.records), 2)


class TimingTestCase(BaseSignInTestCase):
    """The replies of the sign-in held to a floor."""

    @t.override
    def create_project(self) -> AuthProject:
        return FloorProject()

    async def test_a_reply_and_a_refusal_wait_for_the_floor(self) -> None:
        await self.sign_up("a@b.c")
        for start in (AuthTestingStart(subject="a@b.c"), AuthTestingStart(subject="x")):
            with self.subTest(subject=start.subject):
                with mock.patch.object(
                    asyncio, "sleep", new_callable=mock.AsyncMock
                ) as sleep:
                    with contextlib.suppress(AuthMethodRefusedError):
                        await self.start(start)
                (rest,) = sleep.await_args_list[-1].args
                self.assertTrue(0 < rest <= 0.3, rest)

    async def test_an_answer_waits_for_the_floor_too(self) -> None:
        await self.sign_up("a@b.c")
        with mock.patch.object(asyncio, "sleep", new_callable=mock.AsyncMock) as sleep:
            challenge = await self.start(AuthTestingStart(subject="a@b.c", code="1"))
            assert isinstance(challenge, AuthSignInChallenge)
            with self.assertRaises(AuthMethodRefusedError):
                await self.answer(challenge.attempt_uid, "2")
        self.assertEqual(sleep.await_count, 2)


class TimingStrategiesTestCase(unittest.IsolatedAsyncioTestCase):
    def test_the_sign_in_has_no_timing_by_default(self) -> None:
        self.assertIs(AuthSignInUnit.timing.cls, BaseAuthTiming)

    async def test_no_timing_holds_nothing(self) -> None:
        project = TstProject()
        timing = project.auth.sign_in.timing
        self.assertIsInstance(timing, AuthNoTiming)
        with mock.patch.object(asyncio, "sleep", new_callable=mock.AsyncMock) as sleep:
            async with timing.hold():
                pass
        sleep.assert_not_awaited()

    async def test_the_floor_is_of_the_configs(self) -> None:
        project = FloorProject()
        project.settings.configs.apply({"AUTH_SIGN_IN_MIN_DURATION": 0.5})
        with mock.patch.object(asyncio, "sleep", new_callable=mock.AsyncMock) as sleep:
            async with project.auth.sign_in.timing.hold():
                pass
        (rest,) = sleep.await_args_list[-1].args
        self.assertTrue(0.4 < rest <= 0.5, rest)
