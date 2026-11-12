import typing as t
import unittest
from dataclasses import dataclass, field
from unittest import mock

from ingots.defaults.operations import (
    BaseOperation,
    Caller,
    OperationMetadata,
    Permissions,
)
from ingots.puer import BoundFactory, Factories, Factory, Slot, Unit

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.policies import (
    AuthChars,
    AuthCharsConfig,
    AuthCharsPolicy,
    AuthHasValue,
    AuthLengthConfig,
    AuthLengthPolicy,
    AuthPolicyViolationError,
)

LETTERS_AND_DIGITS: t.Final = AuthChars.LETTERS | AuthChars.DIGITS
ANONYMOUS: t.Final = Caller(uid="anonymous", permissions=Permissions())


@dataclass(frozen=True, slots=True, kw_only=True)
class Value:
    value: str = field(repr=False)


class HasCurrent(t.Protocol):
    """Parameters replacing a current value."""

    @property
    def current(self) -> str: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeParameters:
    """The parameters of a change: the parts of the policies of its group."""

    value: str = field(repr=False)
    current: str = field(repr=False)


class HasValueAndCurrent(AuthHasValue, HasCurrent, t.Protocol):
    pass


class ChangedPolicy(BaseOperation[HasValueAndCurrent, None]):
    """A policy of an application, of the parts a change gives."""

    PERMISSIONS = Permissions()

    @t.override
    async def _run(
        self, parameters: HasValueAndCurrent, metadata: OperationMetadata
    ) -> None:
        if parameters.value == parameters.current:
            raise AuthPolicyViolationError.for_policy("changed")


class RangeLength(AuthLengthPolicy):
    CONFIG = AuthLengthConfig(min=2, max=3)


class NicknameChars(AuthCharsPolicy):
    CONFIG = AuthCharsConfig(allowed=LETTERS_AND_DIGITS, extra="_")


class StrongChars(AuthCharsPolicy):
    CONFIG = AuthCharsConfig(required=AuthChars.DIGITS | AuthChars.SYMBOLS)


class TstPoliciesUnit(Unit):
    """The policies and a group of them, as a method holds them."""

    length = Factory(AuthLengthPolicy)
    range_length = Factory(RangeLength)
    chars = Factory(AuthCharsPolicy)
    nickname_chars = Factory(NicknameChars)
    strong_chars = Factory(StrongChars)
    policies_change = Factories[BaseOperation[ChangeParameters, t.Any]](
        RangeLength, ChangedPolicy
    )


class TstAuthUnit(AuthMemoryUnit):
    policies = Slot(TstPoliciesUnit)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class PoliciesTestCase(unittest.IsolatedAsyncioTestCase):
    @property
    def policies(self) -> TstPoliciesUnit:
        return self.project.auth.policies

    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.enterContext(mock.patch("ingots.defaults.operations.runner.logger"))
        self.project = TstProject()
        self.metadata = self.project.operations.create_metadata(ANONYMOUS)

    async def get_broken(
        self, policy: BoundFactory[BaseOperation[Value, None]], value: str
    ) -> str | None:
        """The name of the policy the value breaks, ``None`` if it keeps it."""
        runner = self.project.operations.runner
        try:
            await runner.run(policy, Value(value=value), self.metadata)
        except AuthPolicyViolationError as error:
            return error.policy
        return None

    async def assertBroken(
        self,
        policy: BoundFactory[BaseOperation[Value, None]],
        values: dict[str, str | None],
    ) -> None:
        for value, broken in values.items():
            with self.subTest(value=value):
                self.assertEqual(await self.get_broken(policy, value), broken)

    async def test_a_length_is_between_the_limits(self) -> None:
        await self.assertBroken(
            self.policies.range_length,
            {"a": "length", "ab": None, "abc": None, "abcd": "length"},
        )

    async def test_any_length_is_allowed_unless_told(self) -> None:
        await self.assertBroken(self.policies.length, {"": None, "a" * 1000: None})

    async def test_the_chars_are_of_the_sets_allowed_or_extra(self) -> None:
        await self.assertBroken(
            self.policies.nickname_chars,
            {
                "alice_7": None,
                "алиса": None,
                "ali ce": "chars",
                "ali-ce": "chars",
                "ali\tce": "chars",
            },
        )

    async def test_any_chars_are_allowed_unless_told(self) -> None:
        await self.assertBroken(self.policies.chars, {"a b\t-": None})

    async def test_the_chars_required_are_there(self) -> None:
        await self.assertBroken(
            self.policies.strong_chars,
            {"horse7!": None, "horse7": "chars", "horse!": "chars"},
        )

    def test_a_char_is_in_its_set(self) -> None:
        for char, chars in (
            ("ж", AuthChars.LETTERS),
            ("٣", AuthChars.DIGITS),
            ("²", AuthChars(0)),
            ("€", AuthChars.SYMBOLS),
            ("—", AuthChars.SYMBOLS),
            (" ", AuthChars.SPACES),
            ("\n", AuthChars(0)),
        ):
            with self.subTest(char=char):
                self.assertEqual(AuthChars.of(char), chars)

    async def test_a_group_of_parameters_of_parts_takes_the_policies_of_each(
        self,
    ) -> None:
        group = self.policies.policies_change
        operations = self.project.operations
        results = await operations.run_group(
            group, ChangeParameters(value="al", current="bob"), self.metadata
        )
        self.assertIsNone(results.get(ChangedPolicy))
        for parameters, broken in (
            (ChangeParameters(value="abcd", current="bob"), ["length"]),
            (ChangeParameters(value="bob", current="bob"), ["changed"]),
            (ChangeParameters(value="a", current="a"), ["length", "changed"]),
        ):
            with self.subTest(broken=broken):
                with self.assertRaises(ExceptionGroup) as error:
                    await operations.run_group(group, parameters, self.metadata)
                self.assertEqual(
                    [
                        t.cast(AuthPolicyViolationError, violation).policy
                        for violation in error.exception.exceptions
                    ],
                    broken,
                )

    def test_a_violation_tells_the_policy_only(self) -> None:
        error = AuthPolicyViolationError.for_policy("length")
        self.assertEqual(str(error), "the value breaks the policy 'length'")
        self.assertEqual(error.policy, "length")
