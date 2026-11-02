"""The base of the methods."""

__all__ = ("BaseAuthMethod",)

import typing as t

from ingots.puer import Entity

from .errors import AuthMethodRefusedError, AuthMethodUnsupportedError
from .steps import AuthStep

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthMethod[StartType, AnswerType, StateType](Entity):
    """
    A method of signing up and in: a password, a provider, a code by mail. It
    verifies who it is in steps, each ending with an :class:`AuthChallenge`,
    asking for an answer, or with :class:`AuthVerified`. A method of one step
    verifies at once; what comes before and after the steps, the attempt, the
    profile, the session, is not of the method. A flow starts by a hook of
    its own, as a password is checked against its rules on a sign-up and
    against its hash on a sign-in; the answers go on from the state alone.

    A method is a slot of :class:`AuthMethods`, its name the path of the slot.
    """

    project: "AuthProject"

    @t.final
    def get_name(self) -> str:
        """The name of the method: the path of its slot in the methods."""
        return self.project.auth.methods.slots_find_path(self)

    @t.final
    async def start_sign_up(self, parameters: StartType) -> AuthStep:
        """
        The first step of a sign-up, on what the client starts with.

        :raises AuthMethodUnsupportedError: the method signs no one up.
        :raises AuthMethodRefusedError: the method does not accept it.
        """
        return await self._start_sign_up(parameters)

    @t.final
    async def start_sign_in(self, parameters: StartType) -> AuthStep:
        """
        The first step of a sign-in, on what the client starts with.

        :raises AuthMethodUnsupportedError: the method signs no one in.
        :raises AuthMethodRefusedError: the method does not accept it.
        """
        return await self._start_sign_in(parameters)

    @t.final
    async def answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """
        The next step, on the answer to a challenge and the state it left.

        :raises AuthMethodRefusedError: the method does not accept the answer.
        """
        return await self._answer(state, answer)

    async def _start_sign_up(self, parameters: StartType) -> AuthStep:
        """A method takes the flows it overrides the start of, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_up")

    async def _start_sign_in(self, parameters: StartType) -> AuthStep:
        """A method takes the flows it overrides the start of, none here."""
        raise AuthMethodUnsupportedError.for_flow("sign_in")

    async def _answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """A method of one step asks for nothing, so it takes no answer."""
        raise AuthMethodRefusedError.create()
