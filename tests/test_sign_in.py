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

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
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
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInPermissions,
    AuthSignInResult,
    AuthStartSignInParameters,
)
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpPermissions,
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


class ClosedSignedInGroup(AuthSignedInGroup):
    """Takes the sign-in of every method off the profiles."""

    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()


class ClosedGroupsUnit(AuthGroupsUnit):
    signed_in = Slot(ClosedSignedInGroup)


class ClosedAccessUnit(AuthAccessUnit):
    groups = Slot(ClosedGroupsUnit)


class ClosedAuthUnit(TstAuthUnit):
    access = Slot(ClosedAccessUnit)


class ClosedProject(AuthMemoryProject):
    auth = Slot(ClosedAuthUnit)


class SignInTestCase(unittest.IsolatedAsyncioTestCase):
    project: AuthMemoryProject

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                id=1,
                name="device",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.CLIENT,
            )
        )

    def create_caller(self) -> Caller:
        """The anonymous caller of a server whose flows are open."""
        return Caller(
            uid="anonymous",
            permissions=Permissions(
                AuthSignUpPermissions.CAN_SIGN_UP, AuthSignInPermissions.CAN_SIGN_IN
            )
            | self.project.auth.methods.get_anonymous_permissions(),
        )

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
