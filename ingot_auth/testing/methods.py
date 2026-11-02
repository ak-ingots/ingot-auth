"""
A method for the tests of what is built on the auth: no provider, either
step, a sign-up and a sign-in alike. A test case declares it as a slot of its methods::

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
    The ``secret`` given goes with the verified subject, as it is.
    """

    subject: str
    code: str | None = None
    secret: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthTestingState:
    subject: str
    code: str
    secret: str | None


class AuthTestingMethod(BaseAuthMethod[AuthTestingStart, str, AuthTestingState]):
    """The method of the tests: one step, or two with a code."""

    @t.override
    async def _start_sign_up(self, parameters: AuthTestingStart) -> AuthStep:
        return self._testing_start(parameters)

    @t.override
    async def _start_sign_in(self, parameters: AuthTestingStart) -> AuthStep:
        return self._testing_start(parameters)

    @t.override
    async def _answer(self, state: AuthTestingState, answer: str) -> AuthStep:
        if answer != state.code:
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=state.subject, secret=state.secret)

    @t.final
    def _testing_start(self, parameters: AuthTestingStart) -> AuthStep:
        if parameters.code is None:
            return AuthVerified(subject=parameters.subject, secret=parameters.secret)
        state = AuthTestingState(
            subject=parameters.subject,
            code=parameters.code,
            secret=parameters.secret,
        )
        return AuthChallenge(challenge="code", state=state)
