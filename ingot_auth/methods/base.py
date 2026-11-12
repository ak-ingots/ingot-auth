"""The base of the methods."""

__all__ = ("BaseAuthMethod",)

import typing as t

from ingots.defaults.operations import OperationMetadata, Permissions
from ingots.puer import Unit

from ingot_auth.policies import AuthPolicyViolationError

from .errors import (
    AuthMethodInvalidError,
    AuthMethodRefusedError,
    AuthMethodUnsupportedError,
)
from .steps import AuthStep

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from ingots.defaults.operations import BaseOperation
    from ingots.puer import BoundFactories

    from ingot_auth.project import AuthProject


class BaseAuthMethod[StartType, AnswerType, StateType](Unit):
    """
    A method of signing up and in: a password, a provider, a code by mail. It
    verifies who it is in steps, each ending with an :class:`AuthChallenge`,
    asking for an answer, or with :class:`AuthVerified`. A method of one step
    verifies at once; what comes before and after the steps, the attempt, the
    profile, the session, is not of the method. A flow starts by a hook of
    its own, as a password is checked against its rules on a sign-up and
    against its hash on a sign-in; the answers go on from the state alone.

    A method is a unit: its groups of the policies are its slots
    ``policies_<flow>_<field>``, each of parameters of its own, made by the
    method on the step that checks them. A method is a slot of
    :class:`AuthMethodsUnit`, its name the path of the slot.

    Whether a flow is open is of a hook of its own, ``_get_<flow>_enabled``,
    closed here: a method opens the flows it takes, by the configs of its
    package as a rule, which the project mixes into its own.

    The flows of a method are permissions too, a domain of its own,
    ``auth.methods.nickname``, a flag a flow it takes, ``CAN_SIGN_UP``,
    ``CAN_SIGN_IN``, given by a hook of its own, ``_get_<flow>_permissions``,
    the flow unsupported here: the flow checks the caller has the flag, the
    toggle of the flow gives it, so a flow closed is refused as any operation
    the caller may not run. A method that takes a flow and gives no flag of
    it stays closed, refused as unsupported.

    A method names the kind of the identifier it verifies, ``IDENTIFIER_KIND``:
    the subject it verifies is a value of that kind, bound to a profile once
    whatever method verifies it, so two methods of an email find the same
    profile.
    """

    # the kind of the identifier of the method: nickname, email, phone
    IDENTIFIER_KIND: t.ClassVar[str]

    project: "AuthProject"

    @t.final
    def get_name(self) -> str:
        """The name of the method: the path of its slot in the methods."""
        return self.project.auth.methods.slots_find_path(self)

    @t.final
    def get_sign_up_enabled(self) -> bool:
        """Whether the method signs up, open in the project."""
        return self._get_sign_up_enabled()

    @t.final
    def get_sign_in_enabled(self) -> bool:
        """Whether the method signs in, open in the project."""
        return self._get_sign_in_enabled()

    @t.final
    def get_sign_up_permissions(self) -> Permissions:
        """
        What a caller needs to sign up by the method, ``CAN_SIGN_UP`` of its
        domain, the flow open or not: the flow checks it, the toggle gives it.

        :raises AuthMethodUnsupportedError: the method signs no one up.
        """
        return self._get_sign_up_permissions()

    @t.final
    def get_sign_in_permissions(self) -> Permissions:
        """
        What a caller needs to sign in by the method, ``CAN_SIGN_IN`` of its
        domain, the flow open or not: the flow checks it, the toggle gives it.

        :raises AuthMethodUnsupportedError: the method signs no one in.
        """
        return self._get_sign_in_permissions()

    @t.final
    async def start_sign_up(
        self, parameters: StartType, metadata: OperationMetadata
    ) -> AuthStep:
        """
        The first step of a sign-up, on what the client starts with, for the
        caller of ``metadata``, which the operations the method runs take.

        :raises AuthMethodUnsupportedError: the method signs no one up.
        :raises AuthMethodInvalidError: it breaks policies of the method.
        :raises AuthMethodRefusedError: the method does not accept it.
        """
        return await self._start_sign_up(parameters, metadata)

    @t.final
    async def start_sign_in(
        self, parameters: StartType, metadata: OperationMetadata
    ) -> AuthStep:
        """
        The first step of a sign-in, on what the client starts with, for the
        caller of ``metadata``, which the operations the method runs take.

        :raises AuthMethodUnsupportedError: the method signs no one in.
        :raises AuthMethodRefusedError: the method does not accept it.
        """
        return await self._start_sign_in(parameters, metadata)

    @t.final
    async def answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """
        The next step, on the answer to a challenge and the state it left.

        :raises AuthMethodRefusedError: the method does not accept the answer.
        """
        return await self._answer(state, answer)

    def _get_sign_up_enabled(self) -> bool:
        """A method opens the flows it takes, none here."""
        return False

    def _get_sign_in_enabled(self) -> bool:
        """A method opens the flows it takes, none here."""
        return False

    def _get_sign_up_permissions(self) -> Permissions:
        """A method gives the flag of each flow it takes, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_up")

    def _get_sign_in_permissions(self) -> Permissions:
        """A method gives the flag of each flow it takes, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_in")

    async def _start_sign_up(
        self, parameters: StartType, metadata: OperationMetadata
    ) -> AuthStep:
        """A method takes the flows it overrides the start of, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_up")

    async def _start_sign_in(
        self, parameters: StartType, metadata: OperationMetadata
    ) -> AuthStep:
        """A method takes the flows it overrides the start of, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_in")

    async def _answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """A method of one step asks for nothing, so it takes no answer."""
        raise AuthMethodRefusedError.create()

    @t.final
    async def _check[ParametersType](
        self,
        field: str,
        policies: "BoundFactories[BaseOperation[ParametersType, t.Any]]",
        parameters: ParametersType,
        metadata: OperationMetadata,
    ) -> None:
        """
        Checks a field a client gave by the group of its policies, run
        together with the parameters the method made for them, a reach of the
        subclasses.

        :raises AuthMethodInvalidError: it breaks policies, of the field, each
            named in the order of the group.
        """
        try:
            await self.project.operations.run_group(policies, parameters, metadata)
        except* AuthPolicyViolationError as violations:
            names = tuple(_iter_policies(violations))
            raise AuthMethodInvalidError.for_field(field, names) from violations


def _iter_policies(
    violations: BaseExceptionGroup[AuthPolicyViolationError],
) -> "Iterator[str]":
    # a policy running a group of its own nests the violations of the group
    for violation in violations.exceptions:
        if isinstance(violation, BaseExceptionGroup):
            yield from _iter_policies(violation)
        else:
            yield violation.policy
