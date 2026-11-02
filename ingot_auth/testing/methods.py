"""
A method for the tests of what is built on the auth: no secret, no
provider, either step. A test case declares it as a slot of its methods::

    class AppTestingMethods(AppMethods):
        testing = Slot(AuthTestingMethod)
"""

__all__ = ("AuthTestingMethod", "AuthTestingStart")

import typing as t
from dataclasses import dataclass

from ingot_auth.methods import (
    AuthChallenge,
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthTestingStart:
    """
    The start of the method: ``subject`` is verified at once, or, given a
    ``code``, when the answer repeats it, as a code sent by mail would be.
    """

    subject: str
    code: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthTestingState:
    subject: str
    code: str


class AuthTestingMethod(BaseAuthMethod[AuthTestingStart, str, AuthTestingState]):
    """The method of the tests: one step, or two with a code."""

    @t.override
    async def _start(self, parameters: AuthTestingStart) -> AuthStep:
        if parameters.code is None:
            return AuthVerified(subject=parameters.subject)
        state = AuthTestingState(subject=parameters.subject, code=parameters.code)
        return AuthChallenge(challenge="code", state=state)

    @t.override
    async def _answer(self, state: AuthTestingState, answer: str) -> AuthStep:
        if answer != state.code:
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=state.subject)
