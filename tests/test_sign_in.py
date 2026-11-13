import asyncio
import contextlib
import dataclasses
import hashlib
import typing as t
import unittest
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
    AuthMemoryUnit,
)
from ingot_auth.auth import AuthUnit
from ingot_auth.contrib.caches.memory import AuthMemoryCache
from ingot_auth.contrib.storages.memory import AuthMemoryStorage
from ingot_auth.project import AuthProject
from ingot_auth.access import AuthAccessUnit
from ingot_auth.access.groups import AuthGroupsUnit, AuthSignedInGroup
from ingot_auth.caches import AuthAttemptNotFoundError
from ingot_auth.methods import (
    AuthMethodDeniedError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
)
from ingot_auth.sign_in import (
    AuthAnswerSignInParameters,
    AuthFloorTiming,
    AuthNoTiming,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInPermissions,
    AuthSignInResult,
    AuthSignInUnit,
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
    AuthSessionAttr,
    AuthSessionAttrSource,
)
from ingot_auth.testing.methods import (
    AuthTestingMethod,
    AuthTestingPermissions,
    AuthTestingStart,
)


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


class ClosedGroupsUnit(AuthGroupsUnit):
    grp_signed_in = Slot(ClosedSignedInGroup)


class ClosedAccessUnit(AuthAccessUnit):
    groups = Slot(ClosedGroupsUnit)


class ClosedAuthUnit(TstAuthUnit):
    access = Slot(ClosedAccessUnit)


class ClosedProject(AuthMemoryProject):
    auth = Slot(ClosedAuthUnit)


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
                id=1,
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

    async def answer(self, attempt_id: str, answer: str) -> AuthSignInResult:
        parameters = AuthAnswerSignInParameters(attempt_id=attempt_id, answer=answer)
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
        self.assertEqual((caller.uid, caller.session_id), (uid, result.session_id))
        self.assertEqual(
            caller.permissions, Permissions(AuthTestingPermissions.CAN_SIGN_IN)
        )
        session = await self.project.auth.storage.sessions.find(
            hash_token(result.token)
        )
        self.assertEqual(
            (session.uid, session.method, session.attr_values),
            (uid, "testing", {1: "iPhone"}),
        )
        self.assertNotIn(result.token, repr(result))

    async def test_a_method_of_two_steps_signs_in_by_the_answer(self) -> None:
        uid = await self.sign_up("a@b.c")
        challenge = await self.start(AuthTestingStart(subject="a@b.c", code="1"))
        assert isinstance(challenge, AuthSignInChallenge)
        self.assertEqual(challenge.challenge, "code")
        with self.assertRaises(AuthMethodRefusedError):
            await self.answer(challenge.attempt_id, "2")
        result = await self.answer(challenge.attempt_id, "1")
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
            await self.answer(challenge.attempt_id, "1")

    def test_the_anonymous_caller_gets_the_flag_of_the_sign_in(self) -> None:
        self.assertEqual(
            self.project.auth.sign_in.get_anonymous_permissions(),
            Permissions(AuthSignInPermissions.CAN_SIGN_IN),
        )

    async def test_signing_in_needs_the_flags_of_the_flow_and_the_method(
        self,
    ) -> None:
        await self.sign_up("a@b.c")
        sign_in = self.project.auth.sign_in
        for factory in (sign_in.op_start, sign_in.op_answer):
            self.assertEqual(
                factory.cls.PERMISSIONS, Permissions(AuthSignInPermissions.CAN_SIGN_IN)
            )
        caller = self.create_caller()
        for lacking in (
            AuthSignInPermissions.CAN_SIGN_IN,
            AuthTestingPermissions.CAN_SIGN_IN,
        ):
            with self.subTest(lacking=lacking):
                without = dataclasses.replace(
                    caller, permissions=caller.permissions - Permissions(lacking)
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
                await self.answer(challenge.attempt_id, "2")
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
