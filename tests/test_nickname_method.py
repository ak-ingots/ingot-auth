import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import Caller, Permissions
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.methods.nickname import (
    AuthNicknameSignUpContext,
    AuthNicknameSignUpPreset,
    AuthNicknameMethod,
    AuthNicknameStart,
)
from ingot_auth.methods.password import (
    AuthHasIdentifiers,
    AuthPassword,
    AuthPasswordSetContext,
    AuthPasswordSetPreset,
)
from ingot_auth.methods import (
    AuthMethodInvalidError,
    AuthMethodRefusedError,
    AuthMethodsUnit,
    AuthVerified,
)
from ingot_auth.policies import (
    AuthChars,
    AuthCharsConfig,
    AuthCharsPolicy,
    AuthHasValue,
    AuthLengthConfig,
    AuthLengthPolicy,
    AuthPoliciesUnit,
    AuthPolicyBinding,
    BaseAuthPolicy,
)
from ingot_auth.profiles.identities import AuthIdentity
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpPermissions,
    AuthStartSignUpParameters,
)

SIGNING_UP: t.Final = Caller(
    uid="anonymous", permissions=Permissions(AuthSignUpPermissions.CAN_SIGN_UP)
)


class TstPassword(AuthPassword):
    # cheap for the tests
    SCRYPT_LOG_N = 4


class TstCostlierPassword(TstPassword):
    SCRYPT_LOG_N = 5


class TstMethodsUnit(AuthMethodsUnit):
    nickname = Slot(AuthNicknameMethod)
    password = Slot(TstPassword)


class TstAuthUnit(AuthMemoryUnit):
    methods = Slot(TstMethodsUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class NicknamePreset(AuthNicknameSignUpPreset):
    @t.override
    def _get_bindings(
        self,
    ) -> dict[str, AuthPolicyBinding[AuthNicknameSignUpContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["chars"] = AuthCharsPolicy.bind(
            AuthCharsConfig(allowed=AuthChars.LETTERS | AuthChars.DIGITS)
        )
        return bindings


class HasPasswordAndIdentifiers(AuthHasValue, AuthHasIdentifiers, t.Protocol):
    pass


class NoIdentifierPolicy(BaseAuthPolicy[HasPasswordAndIdentifiers, None]):
    """A policy of an application, of a part the context of the password gives."""

    @t.override
    async def _accepts(self, context: HasPasswordAndIdentifiers, config: None) -> bool:
        password = await context.get_value()
        return not any(i in password for i in await context.get_identifiers())


class PasswordPreset(AuthPasswordSetPreset):
    @t.override
    def _get_bindings(
        self,
    ) -> dict[str, AuthPolicyBinding[AuthPasswordSetContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=8))
        bindings["identifier"] = NoIdentifierPolicy.bind(None)
        return bindings


class TstPoliciesUnit(AuthPoliciesUnit):
    no_identifier = Slot(NoIdentifierPolicy)


class PolicedNicknameMethod(AuthNicknameMethod):
    preset_sign_up_nickname = Slot(NicknamePreset)


class PolicedPassword(TstPassword):
    preset_set = Slot(PasswordPreset)


class PolicedMethodsUnit(TstMethodsUnit):
    nickname = Slot(PolicedNicknameMethod)
    password = Slot(PolicedPassword)


class TstPoliciesAuthUnit(TstAuthUnit):
    methods = Slot(PolicedMethodsUnit)
    policies = Slot(TstPoliciesUnit)


class TstPoliciesProject(TstProject):
    auth = Slot(TstPoliciesAuthUnit)


class TstCostlierMethodsUnit(TstMethodsUnit):
    password = Slot(TstCostlierPassword)


class TstCostlierAuthUnit(TstAuthUnit):
    methods = Slot(TstCostlierMethodsUnit)


class TstCostlierProject(TstProject):
    auth = Slot(TstCostlierAuthUnit)


class NicknameMethodTestCase(unittest.IsolatedAsyncioTestCase):
    project: TstProject

    @property
    def method(self) -> AuthNicknameMethod:
        return t.cast(AuthNicknameMethod, self.project.auth.methods.get("nickname"))

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()

    async def sign_up(self, nickname: str, password: str) -> AuthSignedUp:
        start = AuthStartSignUpParameters(
            method="nickname",
            parameters=AuthNicknameStart(nickname=nickname, password=password),
        )
        metadata = self.project.operations.create_metadata(SIGNING_UP)
        result = await self.project.operations.runner.run(
            self.project.auth.sign_up.op_start, start, metadata
        )
        assert isinstance(result, AuthSignedUp)
        return result

    async def sign_in(self, nickname: str, password: str) -> object:
        start = AuthNicknameStart(nickname=nickname, password=password)
        return await self.method.start_sign_in(start)

    async def test_the_method_is_named_by_its_slot(self) -> None:
        self.assertEqual(self.method.get_name(), "nickname")

    async def test_a_signed_up_nickname_signs_in_with_its_password(self) -> None:
        result = await self.sign_up("alice", "correct horse")
        storage = self.project.auth.storage
        self.assertEqual(
            await storage.profiles.identities.find_uid("nickname", "alice"),
            result.uid,
        )
        self.assertEqual(
            await self.sign_in("alice", "correct horse"), AuthVerified(subject="alice")
        )

    async def test_the_password_is_kept_as_its_hash(self) -> None:
        result = await self.sign_up("alice", "correct horse")
        secret = await self.project.auth.storage.profiles.secrets.get(result.uid)
        self.assertTrue(secret.startswith("$scrypt$ln=4,r=8,p=1$"), secret)
        self.assertNotIn("correct horse", secret)

    async def test_the_password_is_of_the_profile(self) -> None:
        result = await self.sign_up("alice", "correct horse")
        await self.project.auth.storage.profiles.identities.create(
            AuthIdentity(kind="nickname", value="wonder", uid=result.uid)
        )
        self.assertEqual(
            await self.sign_in("wonder", "correct horse"),
            AuthVerified(subject="wonder"),
        )

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
            TstPassword, "_verify", autospec=True, return_value=True
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
            ("alice", "alice-in-wonderland", "password", "identifier"),
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
        result = await self.sign_up("alice", "correct horse")
        costlier = TstCostlierProject()
        secret = await self.project.auth.storage.profiles.secrets.get(result.uid)
        profiles = costlier.auth.storage.profiles
        await profiles.identities.create(
            AuthIdentity(kind="nickname", value="alice", uid=result.uid)
        )
        await profiles.secrets.put(result.uid, secret)
        method = costlier.auth.methods.get("nickname")
        start = AuthNicknameStart(nickname="alice", password="correct horse")
        self.assertEqual(
            await method.start_sign_in(start), AuthVerified(subject="alice")
        )

    async def test_a_context_gives_its_parts_and_shows_none(self) -> None:
        context = AuthPasswordSetContext("correct horse", ("alice",))
        self.assertEqual(await context.get_value(), "correct horse")
        self.assertEqual(await context.get_identifiers(), ("alice",))
        self.assertNotIn("correct horse", repr(context))

    def test_the_password_is_not_in_the_repr(self) -> None:
        start = AuthNicknameStart(nickname="alice", password="correct horse")
        self.assertNotIn("correct horse", repr(start))
