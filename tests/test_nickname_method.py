import typing as t
import unittest
from unittest import mock

from ingots.defaults.operations import (
    BaseOperation,
    Caller,
    OperationMetadata,
    OperationPermissionsError,
    Permissions,
)
from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.methods.nickname import (
    AuthNicknameConfigs,
    AuthNicknameMethod,
    AuthNicknamePermissions,
    AuthNicknameSignUpPolicies,
    AuthNicknameStart,
)
from ingot_auth.methods.password import (
    AuthHasIdentifiers,
    AuthPassword,
    AuthPasswordSetParameters,
    AuthPasswordSetPolicies,
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
    AuthPolicyViolationError,
)
from ingot_auth.settings import AuthSettingsUnit
from ingot_auth.settings.configs import AuthConfigs
from ingot_auth.sign_in import (
    AuthSignedIn,
    AuthSignInPermissions,
    AuthStartSignInParameters,
)
from ingot_auth.sign_up import (
    AuthSignedUp,
    AuthSignUpPermissions,
    AuthStartSignUpParameters,
)
from ingot_auth.storages import AuthIdentity

SIGNING_UP: t.Final = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignUpPermissions.CAN_SIGN_UP, AuthNicknamePermissions.CAN_SIGN_UP
    ),
)
SIGNING_IN: t.Final = Caller(
    uid="anonymous",
    permissions=Permissions(
        AuthSignInPermissions.CAN_SIGN_IN, AuthNicknamePermissions.CAN_SIGN_IN
    ),
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


class TstConfigs(AuthNicknameConfigs, AuthConfigs):
    pass


class TstSettingsUnit(AuthSettingsUnit):
    configs = Slot(TstConfigs)


class TstProject(AuthMemoryProject):
    settings = Slot(TstSettingsUnit)
    auth = Slot(TstAuthUnit)


class NicknameChars(AuthCharsPolicy):
    CONFIG = AuthCharsConfig(allowed=AuthChars.LETTERS | AuthChars.DIGITS)


class HasPasswordAndIdentifiers(AuthHasValue, AuthHasIdentifiers, t.Protocol):
    pass


class NoIdentifierPolicy(BaseOperation[HasPasswordAndIdentifiers, None]):
    """A policy of an application, of a part the parameters of a password give."""

    PERMISSIONS = Permissions()

    @t.override
    async def _run(
        self, parameters: HasPasswordAndIdentifiers, metadata: OperationMetadata
    ) -> None:
        if any(i in parameters.value for i in parameters.identifiers):
            raise AuthPolicyViolationError.for_policy("identifier")


class PasswordLength(AuthLengthPolicy):
    CONFIG = AuthLengthConfig(min=8)


class PolicedNicknameMethod(AuthNicknameMethod):
    policies_sign_up_nickname = AuthNicknameSignUpPolicies(NicknameChars)


class PolicedPassword(TstPassword):
    policies_set = AuthPasswordSetPolicies(PasswordLength, NoIdentifierPolicy)


class PolicedMethodsUnit(TstMethodsUnit):
    nickname = Slot(PolicedNicknameMethod)
    password = Slot(PolicedPassword)


class TstPoliciesAuthUnit(TstAuthUnit):
    methods = Slot(PolicedMethodsUnit)


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
        metadata = self.project.operations.create_metadata(SIGNING_IN)
        return await self.method.start_sign_in(start, metadata)

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

    async def test_a_nickname_signs_in_by_the_flow_and_gets_a_token(self) -> None:
        uid = (await self.sign_up("alice", "correct horse")).uid
        runner = self.project.operations.runner
        metadata = self.project.operations.create_metadata(SIGNING_IN)
        sign_in = self.project.auth.sign_in.op_start
        start = AuthStartSignInParameters(
            method="nickname",
            parameters=AuthNicknameStart(nickname="Alice", password="correct horse"),
        )
        result = await runner.run(sign_in, start, metadata)
        assert isinstance(result, AuthSignedIn)
        caller = await self.project.auth.sessions.authenticate(result.token)
        self.assertEqual((caller.uid, caller.session_id), (uid, result.session_id))
        wrong = AuthStartSignInParameters(
            method="nickname",
            parameters=AuthNicknameStart(nickname="alice", password="wrong horse"),
        )
        with self.assertRaises(AuthMethodRefusedError):
            await runner.run(sign_in, wrong, metadata)

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

    async def test_the_policies_of_the_core_take_any_nickname_and_password(
        self,
    ) -> None:
        for nickname, password in (("a", ""), ("al ice", "x" * 1000)):
            with self.subTest(nickname=nickname, password=password):
                await self.sign_up(nickname, password)

    async def test_a_sign_up_keeps_the_policies_of_the_application(self) -> None:
        self.project = TstPoliciesProject()
        for nickname, password, field, policies in (
            ("al ice", "correct horse", "nickname", ("chars",)),
            ("alice", "short", "password", ("length",)),
            ("alice", "alice-in-wonderland", "password", ("identifier",)),
            ("alice", "alice", "password", ("length", "identifier")),
        ):
            with self.subTest(nickname=nickname, password=password):
                with self.assertRaises(AuthMethodInvalidError) as error:
                    await self.sign_up(nickname, password)
                self.assertEqual(error.exception.field, field)
                self.assertEqual(error.exception.policies, policies)
        await self.sign_up("Ａlice", "correct horse")

    async def test_the_violations_a_policy_nests_are_told_in_their_order(
        self,
    ) -> None:
        self.project = TstPoliciesProject()
        nested = ExceptionGroup(
            "rules",
            [
                AuthPolicyViolationError.for_policy("digit"),
                AuthPolicyViolationError.for_policy("upper"),
            ],
        )
        with mock.patch.object(PasswordLength, "_run", side_effect=nested):
            with self.assertRaises(AuthMethodInvalidError) as error:
                await self.sign_up("alice", "alice")
        self.assertEqual(error.exception.policies, ("digit", "upper", "identifier"))

    async def test_a_policy_failing_otherwise_fails_the_sign_up_as_it_is(
        self,
    ) -> None:
        self.project = TstPoliciesProject()
        guarded = Permissions(AuthNicknamePermissions.CAN_SIGN_IN)
        with mock.patch.object(PasswordLength, "PERMISSIONS", guarded):
            with self.assertRaises(OperationPermissionsError):
                await self.sign_up("alice", "correct horse")
        with mock.patch.object(PasswordLength, "_run", side_effect=OSError("down")):
            with self.assertRaises(ExceptionGroup) as error:
                await self.sign_up("alice", "correct horse")
        self.assertIsInstance(error.exception.exceptions[0], OSError)

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
        metadata = costlier.operations.create_metadata(SIGNING_IN)
        self.assertEqual(
            await method.start_sign_in(start, metadata), AuthVerified(subject="alice")
        )

    def test_the_parameters_of_the_policies_show_none_of_their_parts(self) -> None:
        parameters = AuthPasswordSetParameters(
            value="correct horse", identifiers=("alice",)
        )
        self.assertNotIn("correct horse", repr(parameters))
        self.assertNotIn("alice", repr(parameters))

    def test_the_password_is_not_in_the_repr(self) -> None:
        start = AuthNicknameStart(nickname="alice", password="correct horse")
        self.assertNotIn("correct horse", repr(start))
