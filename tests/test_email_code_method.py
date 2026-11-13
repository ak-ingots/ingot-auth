import asyncio
import re
import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.methods.email_code import (
    AuthEmailCodeConfigs,
    AuthEmailCodeMethod,
    AuthEmailCodePermissions,
    AuthEmailCodeStart,
    AuthEmailCodeState,
    AuthEmailSignUpPolicies,
    AuthSendCodeParameters,
)
from ingot_auth.mailers import AuthMail
from ingot_auth.methods import (
    AuthChallenge,
    AuthCodeChallenge,
    AuthMethodInvalidError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
    AuthVerified,
)
from ingot_auth.policies import AuthLengthConfig, AuthLengthPolicy
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.sign_in import (
    AuthAnswerSignInParameters,
    AuthSignedIn,
    AuthSignInChallenge,
    AuthSignInPermissions,
    AuthStartSignInParameters,
)
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.sign_up import (
    AuthAnswerSignUpParameters,
    AuthSignedUp,
    AuthSignUpChallenge,
    AuthSignUpPermissions,
    AuthSignUpResult,
    AuthStartSignUpParameters,
)

SIGNING_UP: t.Final = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignUpPermissions.CAN_SIGN_UP, AuthEmailCodePermissions.CAN_SIGN_UP
    ),
)
SIGNING_IN: t.Final = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignInPermissions.CAN_SIGN_IN, AuthEmailCodePermissions.CAN_SIGN_IN
    ),
)


class EmailLength(AuthLengthPolicy):
    CONFIG = AuthLengthConfig(max=20)


class TstEmailCodeMethod(AuthEmailCodeMethod):
    policies_sign_up_email = AuthEmailSignUpPolicies(EmailLength)


class TstMethodsUnit(AuthMethodsUnit):
    email_code = Slot(TstEmailCodeMethod)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstConfigs(AuthEmailCodeConfigs, AuthConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit):
    configs = Slot(TstConfigs)


class TstProject(AuthMemoryProject):
    settings = Slot(TstSettingsUnit)
    auth = Slot(TstAuthUnit)


class EmailCodeMethodTestCase(unittest.IsolatedAsyncioTestCase):
    project: TstProject

    @property
    def method(self) -> TstEmailCodeMethod:
        return self.project.auth.methods.email_code

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.metadata = self.project.operations.create_metadata(SIGNING_UP)

    def get_codes(self) -> list[tuple[str, str]]:
        """The emails the codes went to so far, with the codes."""
        codes = []
        for mail in self.project.auth.mailer.get_sent():
            if match := re.match(r"Your code is (\d+)\.", mail.text):
                codes.append((mail.to, match[1]))
        return codes

    def get_denials(self) -> list[str]:
        """The emails told the sign-in is closed so far."""
        mails = self.project.auth.mailer.get_sent()
        return [mail.to for mail in mails if "is closed" in mail.subject]

    async def start(self, email: str) -> AuthSignUpChallenge:
        start = AuthStartSignUpParameters(
            method="email_code", parameters=AuthEmailCodeStart(email=email)
        )
        result = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start, start, self.metadata
        )
        assert isinstance(result, AuthSignUpChallenge)
        await self.project.auth.dispatcher.join()
        return result

    async def answer(self, attempt_id: str, code: str) -> AuthSignUpResult:
        answer = AuthAnswerSignUpParameters(attempt_id=attempt_id, answer=code)
        return await self.project.operations.runner.run(
            self.project.auth.sign_up.op_answer, answer, self.metadata
        )

    async def sign_up(self, email: str) -> AuthSignedUp:
        challenge = await self.start(email)
        result = await self.answer(challenge.attempt_id, self.get_codes()[-1][1])
        assert isinstance(result, AuthSignedUp)
        return result

    async def test_a_sign_up_sends_a_code_and_takes_it_back(self) -> None:
        challenge = await self.start("alice@example.com")
        self.assertEqual(challenge.challenge, AuthCodeChallenge(length=6))
        [(email, code)] = self.get_codes()
        self.assertEqual(email, "alice@example.com")
        self.assertRegex(code, r"^\d{6}$")
        result = await self.answer(challenge.attempt_id, code)
        assert isinstance(result, AuthSignedUp)
        identities = self.project.auth.storage.profiles.identities
        self.assertEqual(
            await identities.find_uid("email", "alice@example.com"), result.uid
        )

    async def test_a_wrong_code_is_refused(self) -> None:
        challenge = await self.start("alice@example.com")
        code = self.get_codes()[-1][1]
        wrong = f"{(int(code) + 1) % 10**6:06d}"
        with self.assertRaises(AuthMethodRefusedError):
            await self.answer(challenge.attempt_id, wrong)
        self.assertIsInstance(
            await self.answer(challenge.attempt_id, code), AuthSignedUp
        )

    async def test_the_email_is_normalized(self) -> None:
        await self.sign_up("  Alice@Example.COM ")
        self.assertEqual(self.get_codes()[-1][0], "alice@example.com")
        identities = self.project.auth.storage.profiles.identities
        await identities.find_uid("email", "alice@example.com")

    async def test_a_sign_up_keeps_the_policies_of_the_email(self) -> None:
        with self.assertRaises(AuthMethodInvalidError) as error:
            await self.start("alice.liddell@example.com")
        self.assertEqual(error.exception.field, "email")
        self.assertEqual(error.exception.policies, ("length",))
        self.assertEqual(self.project.auth.mailer.get_sent(), ())
        await self.sign_up("al@b.c")

    async def test_the_state_keeps_no_code(self) -> None:
        step = await self.method.start_sign_up(
            AuthEmailCodeStart(email="al@b.c"), self.metadata
        )
        assert isinstance(step, AuthChallenge)
        await self.project.auth.dispatcher.join()
        state = t.cast(AuthEmailCodeState, step.state)
        code = self.get_codes()[-1][1]
        self.assertNotIn(code, (state.email, state.digest))
        self.assertNotIn(state.digest, repr(state))

    async def test_a_bound_email_signs_in_by_its_code(self) -> None:
        await self.sign_up("al@b.c")
        step = await self.method.start_sign_in(
            AuthEmailCodeStart(email="AL@b.c"), self.metadata
        )
        assert isinstance(step, AuthChallenge)
        await self.project.auth.dispatcher.join()
        code = self.get_codes()[-1][1]
        self.assertEqual(
            await self.method.answer(step.state, code), AuthVerified(subject="al@b.c")
        )

    async def test_a_sign_in_by_the_code_opens_a_session(self) -> None:
        signed_up = await self.sign_up("al@b.c")
        runner = self.project.operations.runner
        sign_in = self.project.auth.sign_in
        metadata = self.project.operations.create_metadata(SIGNING_IN)
        start = AuthStartSignInParameters(
            method="email_code", parameters=AuthEmailCodeStart(email="al@b.c")
        )
        challenge = await runner.run(sign_in.op_start, start, metadata)
        assert isinstance(challenge, AuthSignInChallenge)
        self.assertEqual(challenge.challenge, AuthCodeChallenge(length=6))
        await self.project.auth.dispatcher.join()
        answer = AuthAnswerSignInParameters(
            attempt_id=challenge.attempt_id, answer=self.get_codes()[-1][1]
        )
        signed_in = await runner.run(sign_in.op_answer, answer, metadata)
        assert isinstance(signed_in, AuthSignedIn)
        caller = await self.project.auth.sessions.authenticate(signed_in.token)
        self.assertEqual(caller.uid, signed_up.uid)

    async def test_an_unbound_email_is_asked_alike_but_sent_nothing(self) -> None:
        grants = type(self.project.auth.access.permissions)
        with mock.patch.object(
            grants, "get_permissions", wraps=grants.get_permissions, autospec=True
        ) as get_permissions:
            step = await self.method.start_sign_in(
                AuthEmailCodeStart(email="al@b.c"), self.metadata
            )
        # the same work as for an email bound
        get_permissions.assert_called_once()
        assert isinstance(step, AuthChallenge)
        await self.project.auth.dispatcher.join()
        self.assertEqual(step.challenge, AuthCodeChallenge(length=6))
        self.assertEqual(self.project.auth.mailer.get_sent(), ())
        for code in ("000000", "123456"):
            with self.assertRaises(AuthMethodRefusedError):
                await self.method.answer(step.state, code)

    async def test_a_profile_denied_is_asked_alike_and_told_by_mail(self) -> None:
        await self.sign_up("al@b.c")
        grants = type(self.project.auth.access.permissions)
        with mock.patch.object(grants, "get_permissions", return_value=Permissions()):
            step = await self.method.start_sign_in(
                AuthEmailCodeStart(email="al@b.c"), self.metadata
            )
        assert isinstance(step, AuthChallenge)
        await self.project.auth.dispatcher.join()
        self.assertEqual(step.challenge, AuthCodeChallenge(length=6))
        self.assertEqual(self.get_denials(), ["al@b.c"])
        [(_, code)] = self.get_codes()  # that of the sign-up alone
        with self.assertRaises(AuthMethodRefusedError):
            await self.method.answer(step.state, code)

    async def test_a_start_replies_before_the_mail_is_sent(self) -> None:
        mailer = self.project.auth.mailer
        sending = asyncio.Event()
        send = type(mailer)._send

        async def send_later(self: t.Any, mail: AuthMail) -> None:
            await sending.wait()
            await send(self, mail)

        with mock.patch.object(type(mailer), "_send", send_later):
            step = await self.method.start_sign_up(
                AuthEmailCodeStart(email="al@b.c"), self.metadata
            )
            self.assertIsInstance(step, AuthChallenge)
            self.assertEqual(mailer.get_sent(), ())
            sending.set()
            await self.project.auth.dispatcher.join()
        self.assertEqual(self.get_codes()[0][0], "al@b.c")

    async def test_a_mail_failing_is_logged_and_the_attempt_stays(self) -> None:
        logger = self.enterContext(
            mock.patch("ingots.defaults.operations.runner.logger")
        )
        mailer = type(self.project.auth.mailer)
        with (
            mock.patch.object(mailer, "_send", side_effect=OSError),
            mock.patch.object(self.method, "_create_code", return_value="123456"),
        ):
            challenge = await self.start("al@b.c")
        [call] = logger.warning.call_args_list
        self.assertEqual(call.args[1], "AuthSendCodeOperation")
        self.assertIsInstance(call.args[2], OSError)
        # the code had it come is good still, as the attempt lives
        result = await self.answer(challenge.attempt_id, "123456")
        self.assertIsInstance(result, AuthSignedUp)

    def test_the_mail_is_plain_english_its_secrets_out_of_its_repr(self) -> None:
        mail = self.method._build_code_mail("al@b.c", "123456")
        self.assertEqual((mail.to, mail.subject), ("al@b.c", "Your code"))
        self.assertIn("Your code is 123456.", mail.text)
        self.assertNotIn("al@b.c", repr(mail))
        self.assertNotIn("123456", repr(mail))
        denial = self.method._build_denial_mail("al@b.c")
        self.assertIn("closed", denial.text)
        self.assertNotIn("al@b.c", repr(denial))

    def test_the_parameters_of_the_mail_keep_their_secrets(self) -> None:
        parameters = AuthSendCodeParameters(
            method="email_code", email="al@b.c", code="123456"
        )
        self.assertNotIn("al@b.c", repr(parameters))
        self.assertNotIn("123456", repr(parameters))

    def test_a_code_is_of_its_length(self) -> None:
        with mock.patch.object(TstEmailCodeMethod, "CODE_LENGTH", 4):
            with mock.patch("secrets.randbelow", return_value=7):
                self.assertEqual(self.method._create_code(), "0007")
