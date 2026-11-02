"""The base of the methods."""

__all__ = ("BaseAuthMethod",)

import abc
import typing as t

from ingots.puer import Entity

from .errors import AuthMethodRefusedError
from .steps import AuthStep


class BaseAuthMethod[StartType, AnswerType, StateType](Entity):
    """
    A method of signing up and in: a password, a provider, a code by mail. It
    verifies who it is in steps, each ending with an :class:`AuthChallenge`,
    asking for an answer, or with :class:`AuthVerified`. A method of one step
    verifies at once; what comes before and after the steps, the attempt, the
    profile, the session, is not of the method.

    A method is a slot of :class:`AuthMethods`, its name the path of the slot.
    """

    @t.final
    async def start(self, parameters: StartType) -> AuthStep:
        """
        The first step, on what the client starts with.

        :raises AuthMethodRefusedError: the method does not accept it.
        """
        return await self._start(parameters)

    @t.final
    async def answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """
        The next step, on the answer to a challenge and the state it left.

        :raises AuthMethodRefusedError: the method does not accept the answer.
        """
        return await self._answer(state, answer)

    @abc.abstractmethod
    async def _start(self, parameters: StartType) -> AuthStep:
        raise NotImplementedError(f"{type(self).__qualname__}._start")

    async def _answer(self, state: StateType, answer: AnswerType) -> AuthStep:
        """A method of one step asks for nothing, so it takes no answer."""
        raise AuthMethodRefusedError.create()
