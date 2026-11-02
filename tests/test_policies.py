import typing as t
import unittest
from dataclasses import dataclass

from ingots.puer import Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.policies import (
    AuthChars,
    AuthCharsConfig,
    AuthCharsPolicy,
    AuthHasValue,
    AuthLengthConfig,
    AuthLengthPolicy,
    AuthPolicies,
    AuthPolicyBinding,
    AuthPolicyNotFoundError,
    AuthPolicyPreset,
    AuthPolicyViolationError,
    AuthValueContext,
    AuthValuePolicyPreset,
    BaseAuthPolicy,
)

LETTERS_AND_DIGITS: t.Final = AuthChars.LETTERS | AuthChars.DIGITS


class HasCurrent(AuthHasValue, t.Protocol):
    """A value replacing the current one."""

    async def get_current(self) -> str: ...


@dataclass(frozen=True, slots=True)
class ChangeContext:
    """The context of a change: the parts of the policies of its preset."""

    value: str
    current: str

    async def get_value(self) -> str:
        return self.value

    async def get_current(self) -> str:
        return self.current


class BannedWordsPolicy(BaseAuthPolicy[AuthHasValue, frozenset[str]]):
    @t.override
    async def _accepts(self, context: AuthHasValue, config: frozenset[str]) -> bool:
        return await context.get_value() not in config


class ChangedPolicy(BaseAuthPolicy[HasCurrent, None]):
    @t.override
    async def _accepts(self, context: HasCurrent, config: None) -> bool:
        return await context.get_value() != await context.get_current()


class UnboundPolicy(BaseAuthPolicy[AuthHasValue, None]):
    @t.override
    async def _accepts(self, context: AuthHasValue, config: None) -> bool:
        return True


class StrictLengthPolicy(AuthLengthPolicy):
    @t.override
    async def _accepts(self, context: AuthHasValue, config: AuthLengthConfig) -> bool:
        value = await context.get_value()
        return value.isascii() and await super()._accepts(context, config)


class NicknamePreset(AuthValuePolicyPreset):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[AuthValueContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=3, max=8))
        bindings["chars"] = AuthCharsPolicy.bind(
            AuthCharsConfig(allowed=LETTERS_AND_DIGITS, extra="._-")
        )
        return bindings


class AppNicknamePreset(NicknamePreset):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[AuthValueContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=5))
        del bindings["chars"]
        bindings["banned"] = BannedWordsPolicy.bind(frozenset({"admin", "root"}))
        return bindings


class ChangePreset(AuthPolicyPreset[ChangeContext]):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[ChangeContext, t.Any]]:
        bindings = super()._get_bindings()
        bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=3))
        bindings["changed"] = ChangedPolicy.bind(None)
        return bindings


class BrokenPreset(AuthPolicyPreset[AuthValueContext]):
    @t.override
    def _get_bindings(self) -> dict[str, AuthPolicyBinding[AuthValueContext, t.Any]]:
        return {"unbound": UnboundPolicy.bind(None)}


class TstPolicies(AuthPolicies):
    policy_banned_words = Slot(BannedWordsPolicy)
    policy_changed = Slot(ChangedPolicy)
    preset_sign_up_nickname = Slot(NicknamePreset)
    preset_app_nickname = Slot(AppNicknamePreset)
    preset_change = Slot(ChangePreset)
    preset_broken = Slot(BrokenPreset)


class TstAuth(AuthMemoryUnit):
    policies = Slot(TstPolicies)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuth)


class StrictPolicies(TstPolicies):
    policy_length = Slot(StrictLengthPolicy)


class StrictAuth(TstAuth):
    policies = Slot(StrictPolicies)


class StrictProject(TstProject):
    auth = Slot(StrictAuth)


class PoliciesTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = TstProject()

    async def assertAccepts[ConfigType](
        self,
        policy: BaseAuthPolicy[AuthHasValue, ConfigType],
        config: ConfigType,
        values: dict[str, bool],
    ) -> None:
        for value, accepted in values.items():
            with self.subTest(value=value):
                context = AuthValueContext(value)
                self.assertEqual(await policy.accepts(context, config), accepted)

    async def test_a_length_is_between_the_limits(self) -> None:
        policy = self.project.auth.policies.find(AuthLengthPolicy)
        await self.assertAccepts(
            policy,
            AuthLengthConfig(min=2, max=3),
            {"a": False, "ab": True, "abc": True, "abcd": False},
        )
        await self.assertAccepts(policy, AuthLengthConfig(), {"a" * 1000: True})

    async def test_the_chars_are_of_the_sets_allowed_or_extra(self) -> None:
        await self.assertAccepts(
            self.project.auth.policies.find(AuthCharsPolicy),
            AuthCharsConfig(allowed=LETTERS_AND_DIGITS, extra="_"),
            {
                "alice_7": True,
                "алиса": True,
                "ali ce": False,
                "ali-ce": False,
                "ali\tce": False,
            },
        )

    async def test_any_chars_are_allowed_unless_told(self) -> None:
        await self.assertAccepts(
            self.project.auth.policies.find(AuthCharsPolicy),
            AuthCharsConfig(),
            {"a b\t-": True},
        )

    async def test_the_chars_required_are_there(self) -> None:
        await self.assertAccepts(
            self.project.auth.policies.find(AuthCharsPolicy),
            AuthCharsConfig(required=AuthChars.DIGITS | AuthChars.SYMBOLS),
            {"horse7!": True, "horse7": False, "horse!": False},
        )

    def test_a_char_is_in_its_set(self) -> None:
        for char, chars in (
            ("ж", AuthChars.LETTERS),
            ("٣", AuthChars.DIGITS),
            ("²", AuthChars(0)),
            ("€", AuthChars.SYMBOLS),
            ("—", AuthChars.SYMBOLS),
            (" ", AuthChars.SPACES),
            ("\n", AuthChars(0)),
        ):
            with self.subTest(char=char):
                self.assertEqual(AuthChars.of(char), chars)

    def test_a_policy_binds_itself_with_a_config(self) -> None:
        config = AuthLengthConfig(min=3)
        self.assertEqual(
            AuthLengthPolicy.bind(config), AuthPolicyBinding(AuthLengthPolicy, config)
        )

    def test_a_policy_is_found_by_its_class(self) -> None:
        policies = self.project.auth.policies
        self.assertIs(policies.find(BannedWordsPolicy), policies.policy_banned_words)

    def test_a_subclass_in_the_slot_is_the_policy_of_its_base(self) -> None:
        project = StrictProject()
        policies = project.auth.policies
        self.assertIsInstance(policies.find(AuthLengthPolicy), StrictLengthPolicy)

    def test_a_policy_in_no_slot_is_not_found(self) -> None:
        with self.assertRaises(AuthPolicyNotFoundError) as error:
            self.project.auth.policies.find(UnboundPolicy)
        name = f"{__name__}.UnboundPolicy"
        self.assertEqual(error.exception.kind, name)
        self.assertEqual(str(error.exception), f"no policy of {name}")


class PresetsTestCase(unittest.IsolatedAsyncioTestCase):
    @property
    def policies(self) -> TstPolicies:
        return self.project.auth.policies

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.project = TstProject()

    async def assertViolates[ContextType](
        self, preset: AuthPolicyPreset[ContextType], context: ContextType, binding: str
    ) -> None:
        with self.assertRaises(AuthPolicyViolationError) as error:
            await preset.check(context)
        self.assertEqual(error.exception.binding, binding)

    async def test_the_presets_of_the_core_bind_nothing(self) -> None:
        project = AuthMemoryProject()
        policies = project.auth.policies
        for preset in (
            policies.preset_sign_up_nickname,
            policies.preset_sign_up_password,
        ):
            self.assertEqual(dict(preset.get_bindings()), {})
            await preset.check(AuthValueContext(""))

    async def test_a_value_keeping_the_policies_passes(self) -> None:
        await self.policies.preset_sign_up_nickname.check(AuthValueContext("alice_7"))

    async def test_the_first_broken_binding_is_told(self) -> None:
        preset = self.policies.preset_sign_up_nickname
        await self.assertViolates(preset, AuthValueContext("a!"), "length")
        await self.assertViolates(preset, AuthValueContext("alice!"), "chars")

    async def test_the_bindings_are_given_in_their_order(self) -> None:
        bindings = self.policies.preset_sign_up_nickname.get_bindings()
        self.assertEqual(list(bindings), ["length", "chars"])
        self.assertEqual(
            bindings["length"],
            AuthLengthPolicy.bind(AuthLengthConfig(min=3, max=8)),
        )
        with self.assertRaises(TypeError):
            bindings["length"] = bindings["chars"]  # type: ignore[index]

    async def test_a_subclass_replaces_drops_and_adds_bindings(self) -> None:
        preset = self.policies.preset_app_nickname
        self.assertEqual(list(preset.get_bindings()), ["length", "banned"])
        await preset.check(AuthValueContext("alice!"))
        await self.assertViolates(preset, AuthValueContext("bob"), "length")
        await self.assertViolates(preset, AuthValueContext("admin"), "banned")

    async def test_a_context_of_parts_takes_the_policies_of_each(self) -> None:
        preset = self.policies.preset_change
        await preset.check(ChangeContext("alice", current="bob"))
        await self.assertViolates(preset, ChangeContext("al", "bob"), "length")
        await self.assertViolates(preset, ChangeContext("bob", "bob"), "changed")

    async def test_a_policy_replaced_in_its_slot_checks_the_bindings(self) -> None:
        self.project = StrictProject()
        preset = self.policies.preset_sign_up_nickname
        await preset.check(AuthValueContext("alice"))
        await self.assertViolates(preset, AuthValueContext("алиса"), "length")

    async def test_a_binding_of_a_policy_in_no_slot_fails(self) -> None:
        with self.assertRaises(AuthPolicyNotFoundError):
            await self.policies.preset_broken.check(AuthValueContext("a"))

    async def test_a_preset_binds_nothing_unless_told(self) -> None:
        preset = AuthPolicyPreset[AuthValueContext](self.project)
        self.assertEqual(dict(preset.get_bindings()), {})
        await preset.check(AuthValueContext("anything"))

    def test_a_violation_tells_the_binding_only(self) -> None:
        error = AuthPolicyViolationError.for_binding("length")
        self.assertEqual(str(error), "the value breaks the policy of 'length'")
