import datetime
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    ANONYMOUS_CALLER,
    Caller,
    OperationPermissionsError,
    Permissions,
)
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.caches.memory import AuthMemoryAttemptsCache
from ingot_auth.methods import (
    AuthAttempt,
    AuthAttemptNotFoundError,
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethods,
    AuthMethodUnsupportedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)
from ingot_auth.profiles.identities import (
    AuthIdentityConflictError,
    AuthIdentityNotFoundError,
)
from ingot_auth.profiles import AuthProfileNotFoundError
from ingot_auth.profiles.secrets import AuthSecretNotFoundError
from ingot_auth.registry import (
    AuthAttrType,
    AuthItemInvalidError,
    AuthItemNotFoundError,
)
from ingot_auth.sessions.attrs import AuthSessionAttr, AuthSessionAttrSource
from ingot_auth.sign_up import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpPermissions,
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)
from ingot_auth.storage import AuthTransactionError
from ingot_auth.testing.methods import AuthTestingMethod, AuthTestingStart

SIGNING_UP: t.Final = Caller(
    uid="anonymous", permissions=Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
)


class OneStepMethod(BaseAuthMethod[str, str, None]):
    @t.override
    async def _start_sign_up(self, parameters: str) -> AuthStep:
        return AuthVerified(subject=parameters)


class NoFlowMethod(BaseAuthMethod[str, str, None]):
    pass


class TstMethods(AuthMethods):
    testing = Slot(AuthTestingMethod)
    one_step = Slot(OneStepMethod)
    no_flow = Slot(NoFlowMethod)


class TstAuth(AuthMemoryUnit):
    methods = Slot(TstMethods)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuth)


class SignUpTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.metadata = self.project.operations.create_metadata(SIGNING_UP)
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

    async def test_the_secret_of_the_method_is_kept(self) -> None:
        secrets = self.project.auth.storage.profiles.secrets
        await self.start(AuthTestingStart(subject="a", secret="hash-a"))
        challenge = await self.start(
            AuthTestingStart(subject="b", code="1234", secret="hash-b")
        )
        assert isinstance(challenge, AuthSignUpChallenge)
        await self.answer(challenge.attempt_id, "1234")
        self.assertEqual(await secrets.get("testing", "a"), "hash-a")
        self.assertEqual(await secrets.get("testing", "b"), "hash-b")

    async def test_no_secret_is_kept_for_a_method_giving_none(self) -> None:
        await self.start(AuthTestingStart(subject="a"))
        with self.assertRaises(AuthSecretNotFoundError):
            await self.project.auth.storage.profiles.secrets.get("testing", "a")

    async def test_a_method_signs_up_only_if_it_takes_the_flow(self) -> None:
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await self.start("a", method="no_flow")
        self.assertEqual(error.exception.flow, "sign_up")
        with self.assertRaises(AuthMethodUnsupportedError) as error:
            await self.project.auth.methods.get("no_flow").start_sign_in("a")
        self.assertEqual(error.exception.flow, "sign_in")

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
        with mock.patch.object(profiles, "_create", side_effect=OSError):
            with self.assertRaises(OSError):
                await self.start(AuthTestingStart(subject="a@b.c", secret="hash"))
        with self.assertRaises(AuthSecretNotFoundError):
            await self.project.auth.storage.profiles.secrets.get("testing", "a@b.c")
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
                AuthSecretNotFoundError.for_method("password"),
                "password: the subject has no secret",
            ),
            (AuthAttemptNotFoundError.create(), "no such attempt"),
            (
                AuthIdentityConflictError.for_method("mail"),
                "mail: the subject is bound already",
            ),
            (
                AuthIdentityNotFoundError.for_method("mail"),
                "mail: the subject is not bound",
            ),
            (AuthProfileNotFoundError.for_uid("a1"), "no profile 'a1'"),
            (AuthSignUpRecordNotFoundError.for_uid("a1"), "no sign-up of 'a1'"),
            (AuthTransactionError.for_not_begun(), "no transaction is begun"),
        ):
            self.assertEqual(str(error), message)
