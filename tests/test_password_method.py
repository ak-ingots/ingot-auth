import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.methods.password import AuthPasswordMethod, AuthPasswordStart
from ingot_auth.contrib.methods.password.scrypt import hash_password, verify_password
from ingot_auth.methods import (
    AuthMethodInvalidError,
    AuthMethodRefusedError,
    AuthMethods,
    AuthVerified,
)
from ingot_auth.policies import (
    AuthChars,
    AuthCharsConfig,
    AuthCharsPolicy,
    AuthLengthConfig,
    AuthLengthPolicy,
    AuthPolicies,
    AuthPolicyBinding,
    AuthValueContext,
    AuthValuePolicyPreset,
)
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpPermissions,
    AuthStartSignUpParameters,
)

SIGNING_UP: t.Final = Caller(
    uid="anonymous", permissions=Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
)


class TstPasswordMethod(AuthPasswordMethod):
    # cheap for the tests
    SCRYPT_LOG_N = 4


class TstCostlierPasswordMethod(TstPasswordMethod):
    SCRYPT_LOG_N = 5


class TstMethods(AuthMethods):
    password = Slot(TstPasswordMethod)


class TstAuth(AuthMemoryUnit):
    methods = Slot(TstMethods)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuth)


class NicknamePreset(AuthValuePolicyPreset):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[AuthValueContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["chars"] = AuthCharsPolicy.bind(
            AuthCharsConfig(allowed=AuthChars.LETTERS | AuthChars.DIGITS)
        )
        return bindings


class PasswordPreset(AuthValuePolicyPreset):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[AuthValueContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=8))
        return bindings


class TstPolicies(AuthPolicies):
    preset_sign_up_nickname = Slot(NicknamePreset)
    preset_sign_up_password = Slot(PasswordPreset)


class TstPoliciesAuth(TstAuth):
    policies = Slot(TstPolicies)


class TstPoliciesProject(TstProject):
    auth = Slot(TstPoliciesAuth)


class TstCostlierMethods(TstMethods):
    password = Slot(TstCostlierPasswordMethod)


class TstCostlierAuth(TstAuth):
    methods = Slot(TstCostlierMethods)


class TstCostlierProject(TstProject):
    auth = Slot(TstCostlierAuth)


class PasswordMethodTestCase(unittest.IsolatedAsyncioTestCase):
    project: TstProject

    @property
    def method(self) -> AuthPasswordMethod:
        return t.cast(AuthPasswordMethod, self.project.auth.methods.get("password"))

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()

    async def sign_up(self, nickname: str, password: str) -> AuthSignedUp:
        start = AuthStartSignUpParameters(
            method="password",
            parameters=AuthPasswordStart(nickname=nickname, password=password),
        )
        metadata = self.project.operations.create_metadata(SIGNING_UP)
        result = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start, start, metadata
        )
        assert isinstance(result, AuthSignedUp)
        return result

    async def sign_in(self, nickname: str, password: str) -> object:
        start = AuthPasswordStart(nickname=nickname, password=password)
        return await self.method.start_sign_in(start)

    async def test_the_method_is_named_by_its_slot(self) -> None:
        self.assertEqual(self.method.get_name(), "password")

    async def test_a_signed_up_nickname_signs_in_with_its_password(self) -> None:
        result = await self.sign_up("alice", "correct horse")
        storage = self.project.auth.storage
        self.assertEqual(
            await storage.profile.identities.find_uid("password", "alice"),
            result.uid,
        )
        self.assertEqual(
            await self.sign_in("alice", "correct horse"), AuthVerified(subject="alice")
        )

    async def test_the_password_is_kept_as_its_hash(self) -> None:
        await self.sign_up("alice", "correct horse")
        secret = await self.project.auth.storage.profile.secrets.get(
            "password", "alice"
        )
        self.assertTrue(secret.startswith("$scrypt$ln=4,r=8,p=1$"), secret)
        self.assertNotIn("correct horse", secret)

    async def test_the_nickname_is_normalized(self) -> None:
        await self.sign_up("Ａlice", "correct horse")
        for nickname in ("alice", "ALICE", "Ａｌｉｃｅ"):
            self.assertEqual(
                await self.sign_in(nickname, "correct horse"),
                AuthVerified(subject="alice"),
            )

    async def test_the_password_is_normalized(self) -> None:
        await self.sign_up("alice", "ｃｏｒｒｅｃｔ horse")
        self.assertIsInstance(
            await self.sign_in("alice", "correct horse"), AuthVerified
        )

    async def test_a_wrong_password_and_an_unknown_nickname_are_refused(
        self,
    ) -> None:
        await self.sign_up("alice", "correct horse")
        for nickname, password in (("alice", "Correct horse"), ("bob", "x")):
            with self.assertRaises(AuthMethodRefusedError):
                await self.sign_in(nickname, password)

    async def test_an_unknown_nickname_is_verified_against_a_dummy(self) -> None:
        with mock.patch.object(
            TstPasswordMethod, "_verify", autospec=True, return_value=True
        ) as verify:
            for _ in range(2):
                with self.assertRaises(AuthMethodRefusedError):
                    await self.sign_in("bob", "x")
        self.assertEqual(verify.call_count, 2)
        secrets = {call.args[2] for call in verify.call_args_list}
        self.assertEqual(len(secrets), 1)

    async def test_the_presets_of_the_core_take_any_nickname_and_password(
        self,
    ) -> None:
        for nickname, password in (("a", ""), ("al ice", "x" * 1000)):
            with self.subTest(nickname=nickname, password=password):
                await self.sign_up(nickname, password)

    async def test_a_sign_up_keeps_the_presets_of_the_application(self) -> None:
        self.project = TstPoliciesProject()
        for nickname, password, field, binding in (
            ("al ice", "correct horse", "nickname", "chars"),
            ("alice", "short", "password", "length"),
        ):
            with self.subTest(nickname=nickname, password=password):
                with self.assertRaises(AuthMethodInvalidError) as error:
                    await self.sign_up(nickname, password)
                self.assertEqual(error.exception.field, field)
                self.assertEqual(error.exception.binding, binding)
        await self.sign_up("Ａlice", "correct horse")

    async def test_a_value_is_checked_normalized(self) -> None:
        self.project = TstPoliciesProject()
        # eight characters once normalized, the ligature of two
        await self.sign_up("alice", "\ufb01ve-six")

    async def test_a_hash_of_other_parameters_is_verified(self) -> None:
        await self.sign_up("alice", "correct horse")
        costlier = TstCostlierProject()
        secret = await self.project.auth.storage.profile.secrets.get(
            "password", "alice"
        )
        await costlier.auth.storage.profile.secrets.put("password", "alice", secret)
        method = costlier.auth.methods.get("password")
        start = AuthPasswordStart(nickname="alice", password="correct horse")
        self.assertEqual(
            await method.start_sign_in(start), AuthVerified(subject="alice")
        )

    def test_the_password_is_not_in_the_repr(self) -> None:
        start = AuthPasswordStart(nickname="alice", password="correct horse")
        self.assertNotIn("correct horse", repr(start))


class ScryptTestCase(unittest.TestCase):
    def test_a_hash_verifies_its_password_only(self) -> None:
        secret = hash_password("correct horse", 4, 8, 1)
        self.assertTrue(verify_password("correct horse", secret))
        self.assertFalse(verify_password("correct horsE", secret))

    def test_a_password_gets_a_new_salt_each_time(self) -> None:
        self.assertNotEqual(hash_password("x", 4, 8, 1), hash_password("x", 4, 8, 1))

    def test_what_is_not_a_hash_verifies_nothing(self) -> None:
        secret = hash_password("x", 4, 8, 1)
        _, _, parameters, salt, digest = secret.split("$")
        for other in (
            "",
            "x" + secret,
            secret.replace("$scrypt$", "$argon2id$"),
            f"$scrypt$ln=4,r=8${salt}${digest}",
            f"$scrypt$ln=four,r=8,p=1${salt}${digest}",
            f"$scrypt${parameters}$!!${digest}",
        ):
            with self.subTest(other=other):
                self.assertFalse(verify_password("x", other))
