import dataclasses
import datetime
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    ANONYMOUS_CALLER,
    Caller,
    OperationPermissionsError,
    PermissionFlags,
    Permissions,
)
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.caches import AuthAttempt, AuthAttemptNotFoundError
from ingot_auth.contrib.caches.memory import AuthMemoryAttemptsCache
from ingot_auth.methods import (
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
    AuthMethodUnsupportedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.sign_up import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpPermissions,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from ingot_auth.sign_up.operations import BaseAuthSignUpOperation
from ingot_auth.storages import (
    AuthAttrType,
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
    AuthItemNotFoundError,
    AuthProfileNotFoundError,
    AuthSecretNotFoundError,
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    AuthTransactionError,
)
from ingot_auth.testing.methods import (
    AuthTestingMethod,
    AuthTestingPermissions,
    AuthTestingStart,
)


class OneStepPermissions(PermissionFlags, domain="tests.one_step"):
    CAN_SIGN_UP = 1 << 0


class OneStepMethod(BaseAuthMethod[str, str, None]):
    # of the kind of the testing method: they share its identifiers
    IDENTIFIER_KIND = "testing"

    @t.override
    def _get_sign_up_enabled(self) -> bool:
        return True

    @t.override
    def _get_sign_up_permissions(self) -> Permissions:
        return Permissions(OneStepPermissions.CAN_SIGN_UP)

    @t.override
    async def _start_sign_up(self, parameters: str) -> AuthStep:
        return AuthVerified(subject=parameters)


class NoFlowMethod(BaseAuthMethod[str, str, None]):
    pass


class NoFlagMethod(BaseAuthMethod[str, str, None]):
    # starts a sign-up, but gives no flag of it
    IDENTIFIER_KIND = "testing"

    @t.override
    async def _start_sign_up(self, parameters: str) -> AuthStep:
        return AuthVerified(subject=parameters)


class TstMethodsUnit(AuthMethodsUnit):
    testing = Slot(AuthTestingMethod)
    one_step = Slot(OneStepMethod)
    no_flow = Slot(NoFlowMethod)
    no_flag = Slot(NoFlagMethod)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class SignUpTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        # the anonymous caller of a server whose sign-up is open
        self.caller = Caller(
            uid="anonymous",
            permissions=Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
            | self.project.auth.methods.get_anonymous_permissions(),
        )
        self.metadata = self.project.operations.create_metadata(self.caller)
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                id=1,
                name="device",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.CLIENT,
            )
        )
        await self.project.auth.storage.sessions.attrs.create(
            AuthSessionAttr(
                id=2,
                name="ip",
                type=AuthAttrType.STR,
                source=AuthSessionAttrSource.TRANSPORT,
            )
        )

    async def start(
        self, parameters: object, method: str = "testing", **values: t.Any
    ) -> AuthSignUpResult:
        start = AuthStartSignUpParameters(
            method=method,
            parameters=parameters,
            values={int(key.removeprefix("a")): value for key, value in values.items()},
        )
        return await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start, start, self.metadata
        )

    async def answer(self, attempt_id: str, answer: object) -> AuthSignUpResult:
        parameters = AuthAnswerSignUpParameters(attempt_id=attempt_id, answer=answer)
        return await self.project.operations.runner.run(
            self.project.auth.sign_up.op_answer, parameters, self.metadata
        )

    async def test_a_method_of_one_step_signs_up_at_once(self) -> None:
        result = await self.start(AuthTestingStart(subject="a@b.c"), a1="iPhone")
        assert isinstance(result, AuthSignedUp)
        storage = self.project.auth.storage
        self.assertEqual(
            await storage.profiles.identities.find_uid("testing", "a@b.c"), result.uid
        )
        profile = await storage.profiles.get(result.uid)
        record = await storage.sign_up.records.get(result.uid)
        self.assertEqual(
            record,
            AuthSignUpRecord(
                uid=result.uid,
                method="testing",
                signed_up_at=profile.created_at,
                values={1: "iPhone"},
            ),
        )

    async def test_a_challenge_is_answered_to_its_attempt(self) -> None:
        challenge = await self.start(
            AuthTestingStart(subject="a@b.c", code="1234"), a1="iPhone"
        )
        assert isinstance(challenge, AuthSignUpChallenge)
        self.assertEqual(challenge.challenge, "code")
        result = await self.answer(challenge.attempt_id, "1234")
        assert isinstance(result, AuthSignedUp)
        record = await self.project.auth.storage.sign_up.records.get(result.uid)
        self.assertEqual(record.values, {1: "iPhone"})
        with self.assertRaises(AuthAttemptNotFoundError):
            await self.answer(challenge.attempt_id, "1234")

    async def test_the_secret_of_the_method_is_kept_as_of_the_profile(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        first = await self.start(AuthTestingStart(subject="a", secret="hash-a"))
        challenge = await self.start(
            AuthTestingStart(subject="b", code="1234", secret="hash-b")
        )
        assert isinstance(challenge, AuthSignUpChallenge)
        second = await self.answer(challenge.attempt_id, "1234")
        assert isinstance(first, AuthSignedUp) and isinstance(second, AuthSignedUp)
        self.assertEqual(await secrets.get(first.uid), "hash-a")
        self.assertEqual(await secrets.get(second.uid), "hash-b")

    async def test_no_secret_is_kept_for_a_method_giving_none(self) -> None:
        result = await self.start(AuthTestingStart(subject="a"))
        assert isinstance(result, AuthSignedUp)
        with self.assertRaises(AuthSecretNotFoundError):
            await self.project.auth.storage.profiles.secrets.get(result.uid)

    async def test_an_identifier_is_bound_once_whatever_method_of_its_kind(
        self,
    ) -> None:
        await self.start(AuthTestingStart(subject="a@b.c"))
        with self.assertRaises(AuthIdentityConflictError) as error:
            await self.start("a@b.c", method="one_step")
        self.assertEqual(error.exception.kind, "testing")

    async def test_a_method_signs_up_only_if_it_takes_the_flow(self) -> None:
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await self.start("a", method="no_flow")
        self.assertEqual(error.exception.flow, "sign_up")
        no_flow = self.project.auth.methods.get("no_flow")
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await no_flow.start_sign_up("a")
        self.assertEqual(error.exception.flow, "sign_up")
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await no_flow.start_sign_in("a")
        self.assertEqual(error.exception.flow, "sign_in")

    async def test_a_flow_whose_method_gives_no_flag_of_it_stays_closed(
        self,
    ) -> None:
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await self.start("a", method="no_flag")
        self.assertEqual(error.exception.flow, "sign_up")

    async def test_the_testing_method_signs_in_as_it_signs_up(self) -> None:
        method = self.project.auth.methods.get("testing")
        step = await method.start_sign_in(AuthTestingStart(subject="a", secret="h"))
        self.assertEqual(step, AuthVerified(subject="a", secret="h"))

    async def test_a_refused_answer_keeps_the_attempt_until_the_limit(self) -> None:
        challenge = await self.start(AuthTestingStart(subject="a", code="1234"))
        assert isinstance(challenge, AuthSignUpChallenge)
        for _ in range(4):
            with self.assertRaises(AuthMethodRefusedError):
                await self.answer(challenge.attempt_id, "0000")
        result = await self.answer(challenge.attempt_id, "1234")
        self.assertIsInstance(result, AuthSignedUp)

    async def test_the_attempt_is_over_after_the_last_refused_answer(self) -> None:
        challenge = await self.start(AuthTestingStart(subject="a", code="1234"))
        assert isinstance(challenge, AuthSignUpChallenge)
        for _ in range(5):
            with self.assertRaises(AuthMethodRefusedError):
                await self.answer(challenge.attempt_id, "0000")
        with self.assertRaises(AuthAttemptNotFoundError):
            await self.answer(challenge.attempt_id, "1234")

    async def test_an_expired_attempt_is_not_found(self) -> None:
        challenge = await self.start(AuthTestingStart(subject="a", code="1234"))
        assert isinstance(challenge, AuthSignUpChallenge)
        later = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=11)
        with mock.patch.object(AuthMemoryAttemptsCache, "_get_now", return_value=later):
            with self.assertRaises(AuthAttemptNotFoundError):
                await self.answer(challenge.attempt_id, "1234")

    async def test_an_attempt_of_another_flow_is_not_found(self) -> None:
        await self.project.auth.cache.attempts.put(
            AuthAttempt(
                id="x",
                flow="sign_in",
                method="testing",
                state=None,
                values={},
                expires_at=datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=1),
            )
        )
        with self.assertRaises(AuthAttemptNotFoundError):
            await self.answer("x", "1234")

    async def test_a_subject_signs_up_once(self) -> None:
        await self.start(AuthTestingStart(subject="a@b.c"))
        with self.assertRaises(AuthIdentityConflictError):
            await self.start(AuthTestingStart(subject="a@b.c"))

    async def test_a_sign_up_failing_midway_leaves_nothing(self) -> None:
        profiles = type(self.project.auth.storage.profiles)
        with (
            mock.patch.object(profiles, "_create", side_effect=OSError),
            mock.patch.object(
                BaseAuthSignUpOperation, "_create_uid", return_value="a1"
            ),
        ):
            with self.assertRaises(OSError):
                await self.start(AuthTestingStart(subject="a@b.c", secret="hash"))
        with self.assertRaises(AuthSecretNotFoundError):
            await self.project.auth.storage.profiles.secrets.get("a1")
        result = await self.start(AuthTestingStart(subject="a@b.c"))
        self.assertIsInstance(result, AuthSignedUp)

    async def test_an_unknown_method_is_not_found(self) -> None:
        with self.assertRaises(AuthMethodNotFoundError) as error:
            await self.start("a", method="password")
        self.assertEqual(error.exception.name, "password")

    async def test_the_values_are_the_clients_and_of_their_types(self) -> None:
        for values, error_cls in (
            ({"a3": "x"}, AuthItemNotFoundError),
            ({"a2": "10.0.0.1"}, AuthItemInvalidError),
            ({"a1": 7}, AuthItemInvalidError),
        ):
            with self.assertRaises(error_cls):
                await self.start(AuthTestingStart(subject="a"), **values)

    async def test_a_method_of_one_step_takes_no_answer(self) -> None:
        method = self.project.auth.methods.get("one_step")
        with self.assertRaises(AuthMethodRefusedError):
            await method.answer(None, "x")
        result = await self.start("a", method="one_step")
        self.assertIsInstance(result, AuthSignedUp)

    async def test_signing_up_needs_its_permission(self) -> None:
        sign_up = self.project.auth.sign_up
        for factory in (sign_up.op_start, sign_up.op_answer):
            self.assertEqual(
                factory.cls.PERMISSIONS, Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
            )
        self.metadata = self.project.operations.create_metadata(ANONYMOUS_CALLER)
        with self.assertRaises(OperationPermissionsError):
            await self.start(AuthTestingStart(subject="a"))

    async def test_the_anonymous_caller_gets_the_flags_of_the_methods_open(
        self,
    ) -> None:
        self.assertEqual(
            self.project.auth.methods.get_anonymous_permissions(),
            Permissions(
                AuthTestingPermissions.CAN_SIGN_UP | AuthTestingPermissions.CAN_SIGN_IN,
                OneStepPermissions.CAN_SIGN_UP,
            ),
        )

    async def test_signing_up_by_a_method_needs_its_flag(self) -> None:
        challenge = await self.start(AuthTestingStart(subject="a", code="1"))
        assert isinstance(challenge, AuthSignUpChallenge)
        self.metadata = self.project.operations.create_metadata(
            dataclasses.replace(
                self.caller,
                permissions=self.caller.permissions
                - Permissions(AuthTestingPermissions.CAN_SIGN_UP),
            )
        )
        with self.assertRaises(OperationPermissionsError) as error:
            await self.start(AuthTestingStart(subject="b"))
        self.assertEqual(
            error.exception.required, Permissions(AuthTestingPermissions.CAN_SIGN_UP)
        )
        # an attempt is of a method closed meanwhile
        with self.assertRaises(OperationPermissionsError):
            await self.answer(challenge.attempt_id, "1")
        self.assertIsInstance(await self.start("c", method="one_step"), AuthSignedUp)


class MethodPermissionsTestCase(unittest.TestCase):
    def test_a_flow_needs_its_flag_whether_open_or_not(self) -> None:
        project = TstProject()
        one_step = project.auth.methods.get("one_step")
        self.assertEqual(
            one_step.get_sign_up_permissions(),
            Permissions(OneStepPermissions.CAN_SIGN_UP),
        )
        no_flow = project.auth.methods.get("no_flow")
        for get in (no_flow.get_sign_up_permissions, no_flow.get_sign_in_permissions):
            with self.assertRaises(AuthMethodUnsupportedError):
                get()


class ErrorsTestCase(unittest.TestCase):
    def test_an_error_tells_its_message_and_no_subject(self) -> None:
        for error, message in (
            (AuthMethodNotFoundError.for_name("x"), "no method 'x'"),
            (AuthMethodRefusedError.create(), "the method refuses"),
            (
                AuthMethodInvalidError.for_field("password", "length"),
                "the password breaks the policy of 'length'",
            ),
            (
                AuthMethodUnsupportedError.for_flow("sign_in"),
                "the method takes no sign_in",
            ),
            (
                AuthSecretNotFoundError.for_uid("a1"),
                "the profile 'a1' has no secret",
            ),
            (AuthAttemptNotFoundError.create(), "no such attempt"),
            (
                AuthIdentityConflictError.for_kind("email"),
                "email: the identifier is bound already",
            ),
            (
                AuthIdentityNotFoundError.for_kind("email"),
                "email: the identifier is not bound",
            ),
            (AuthProfileNotFoundError.for_uid("a1"), "no profile 'a1'"),
            (AuthSignUpRecordNotFoundError.for_uid("a1"), "no sign-up of 'a1'"),
            (AuthTransactionError.for_not_begun(), "no transaction is begun"),
        ):
            self.assertEqual(str(error), message)
