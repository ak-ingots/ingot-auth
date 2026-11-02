import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Project, Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.methods.email import (
    AuthEmailChallenge,
    AuthEmailSignUpContext,
    AuthEmailSignUpPreset,
    AuthEmailStart,
    AuthEmailState,
    BaseAuthEmailMethod,
)
from ingot_auth.methods import (
    AuthChallenge,
    AuthMethodInvalidError,
    AuthMethodRefusedError,
    AuthMethods,
    AuthVerified,
)
from ingot_auth.policies import (
    AuthLengthConfig,
    AuthLengthPolicy,
    AuthPolicyBinding,
)
from ingot_auth.sign_up import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpPermissions,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)

SIGNING_UP: t.Final = Caller(
    uid="anonymous", permissions=Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
)


class EmailPreset(AuthEmailSignUpPreset):
    @t.override
    def _get_bindings(
        self,
    ) -> dict[str, AuthPolicyBinding[AuthEmailSignUpContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(max=20))
        return bindings


class TstEmailMethod(BaseAuthEmailMethod):
    """Keeps the mail it sends, for the tests to read."""

    preset_sign_up_email = Slot(EmailPreset)

    def __init__(self, project: Project) -> None:
        super().__init__(project)
        self.sent: list[tuple[str, str]] = []

    @t.override
    async def _send_code(self, email: str, code: str) -> None:
        self.sent.append((email, code))


class TstMethods(AuthMethods):
    email = Slot(TstEmailMethod)


class TstAuth(AuthMemoryUnit):
    methods = Slot(TstMethods)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuth)


class EmailMethodTestCase(unittest.IsolatedAsyncioTestCase):
    project: TstProject

    @property
    def method(self) -> TstEmailMethod:
        return self.project.auth.methods.email

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.metadata = self.project.operations.create_metadata(SIGNING_UP)

    async def start(self, email: str) -> AuthSignUpChallenge:
        start = AuthStartSignUpParameters(
            method="email", parameters=AuthEmailStart(email=email)
        )
        result = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start, start, self.metadata
        )
        assert isinstance(result, AuthSignUpChallenge)
        return result

    async def answer(self, attempt_id: str, code: str) -> AuthSignUpResult:
        answer = AuthAnswerSignUpParameters(attempt_id=attempt_id, answer=code)
        return await self.project.operations.runner.run(
            self.project.auth.sign_up.op_answer, answer, self.metadata
        )

    async def sign_up(self, email: str) -> AuthSignedUp:
        challenge = await self.start(email)
        result = await self.answer(challenge.attempt_id, self.method.sent[-1][1])
        assert isinstance(result, AuthSignedUp)
        return result

    async def test_a_sign_up_sends_a_code_and_takes_it_back(self) -> None:
        challenge = await self.start("alice@example.com")
        self.assertEqual(challenge.challenge, AuthEmailChallenge(length=6))
        [(email, code)] = self.method.sent
        self.assertEqual(email, "alice@example.com")
        self.assertRegex(code, r"^\d{6}$")
        result = await self.answer(challenge.attempt_id, code)
        assert isinstance(result, AuthSignedUp)
        identities = self.project.auth.storage.profile.identities
        self.assertEqual(
            await identities.find_uid("email", "alice@example.com"), result.uid
        )

    async def test_a_wrong_code_is_refused(self) -> None:
        challenge = await self.start("alice@example.com")
        code = self.method.sent[-1][1]
        wrong = f"{(int(code) + 1) % 10**6:06d}"
        with self.assertRaises(AuthMethodRefusedError):
            await self.answer(challenge.attempt_id, wrong)
        self.assertIsInstance(
            await self.answer(challenge.attempt_id, code), AuthSignedUp
        )

    async def test_the_email_is_normalized(self) -> None:
        await self.sign_up("  Alice@Example.COM ")
        self.assertEqual(self.method.sent[-1][0], "alice@example.com")
        identities = self.project.auth.storage.profile.identities
        await identities.find_uid("email", "alice@example.com")

    async def test_a_sign_up_keeps_the_preset_of_the_email(self) -> None:
        with self.assertRaises(AuthMethodInvalidError) as error:
            await self.start("alice.liddell@example.com")
        self.assertEqual(error.exception.field, "email")
        self.assertEqual(error.exception.binding, "length")
        self.assertEqual(self.method.sent, [])
        await self.sign_up("al@b.c")

    async def test_the_state_keeps_no_code(self) -> None:
        step = await self.method.start_sign_up(AuthEmailStart(email="al@b.c"))
        assert isinstance(step, AuthChallenge)
        state = t.cast(AuthEmailState, step.state)
        code = self.method.sent[-1][1]
        self.assertNotIn(code, (state.email, state.digest))
        self.assertNotIn(state.digest, repr(state))

    async def test_a_bound_email_signs_in_by_its_code(self) -> None:
        await self.sign_up("al@b.c")
        step = await self.method.start_sign_in(AuthEmailStart(email="AL@b.c"))
        assert isinstance(step, AuthChallenge)
        code = self.method.sent[-1][1]
        self.assertEqual(
            await self.method.answer(step.state, code), AuthVerified(subject="al@b.c")
        )

    async def test_an_unbound_email_is_asked_alike_but_sent_nothing(self) -> None:
        step = await self.method.start_sign_in(AuthEmailStart(email="al@b.c"))
        assert isinstance(step, AuthChallenge)
        self.assertEqual(step.challenge, AuthEmailChallenge(length=6))
        self.assertEqual(self.method.sent, [])
        for code in ("000000", "123456"):
            with self.assertRaises(AuthMethodRefusedError):
                await self.method.answer(step.state, code)

    def test_a_code_is_of_its_length(self) -> None:
        with mock.patch.object(TstEmailMethod, "CODE_LENGTH", 4):
            with mock.patch("secrets.randbelow", return_value=7):
                self.assertEqual(self.method._create_code(), "0007")
