"""
The method of an email and a code sent to it, of two steps: the start sends
the code, the answer repeats it. The core sends no mail: an application
extends :class:`BaseAuthEmailMethod` with the sending, by the mail of its
own, and declares it as a slot of its methods,
``email = Slot(AppEmailMethod)``. The email of a sign-up is checked by the
preset of the policies of the method, its slot ``preset_sign_up_email``,
empty unless an application binds policies to it in its subclass.
"""

__all__ = (
    "AuthEmailChallenge",
    "AuthEmailSignUpContext",
    "AuthEmailSignUpPreset",
    "AuthEmailStart",
    "AuthEmailState",
    "BaseAuthEmailMethod",
)

import abc
import hashlib
import hmac
import secrets
import typing as t
import unicodedata
from dataclasses import dataclass, field

from ingots.puer import Slot

from ingot_auth.methods import (
    AuthChallenge,
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)
from ingot_auth.profile.identities import AuthIdentityNotFoundError

from .contexts import AuthEmailSignUpContext
from .presets import AuthEmailSignUpPreset


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailStart:
    """What a sign-up and a sign-in start with: an email."""

    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailChallenge:
    """The code is sent: the client answers with it, of ``length`` digits."""

    length: int


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailState:
    """
    What the server keeps till the answer: the email and the digest of the
    code, not the code, for the cache may be read by more than the server.
    """

    email: str
    digest: str = field(repr=False)


class BaseAuthEmailMethod(BaseAuthMethod[AuthEmailStart, str, AuthEmailState]):
    """
    An email and a code of :attr:`CODE_LENGTH` digits sent to it by
    :meth:`_send_code`, the hook an application implements. The email is
    normalized to NFKC and case-folded: the subject is the email normalized.
    The code is good for the attempt, as long as it lives and till the
    answers refused reach their limit.

    A sign-in sends the code only to an email bound to a profile, and asks
    for it all the same otherwise, so that the answer tells nothing of the
    email: no code is then good.
    """

    CODE_LENGTH: t.ClassVar[int] = 6

    preset_sign_up_email = Slot(AuthEmailSignUpPreset)

    @t.override
    async def _start_sign_up(self, parameters: AuthEmailStart) -> AuthStep:
        email = self._normalize_email(parameters.email)
        await self._check(
            "email", self.preset_sign_up_email, AuthEmailSignUpContext(email)
        )
        return await self._send(email)

    @t.override
    async def _start_sign_in(self, parameters: AuthEmailStart) -> AuthStep:
        email = self._normalize_email(parameters.email)
        identities = self.project.auth.storage.profile.identities
        try:
            await identities.find_uid(self.get_name(), email)
        except AuthIdentityNotFoundError:
            return self._ask(email, self._create_code())
        return await self._send(email)

    @t.override
    async def _answer(self, state: AuthEmailState, answer: str) -> AuthStep:
        if not hmac.compare_digest(self._digest(answer), state.digest):
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=state.email)

    @abc.abstractmethod
    async def _send_code(self, email: str, code: str) -> None:
        """Sends the code to the email, by the mail of the application."""
        raise NotImplementedError(f"{type(self).__qualname__}._send_code")

    def _normalize_email(self, email: str) -> str:
        return unicodedata.normalize("NFKC", email).strip().casefold()

    def _create_code(self) -> str:
        """A code of random digits."""
        return f"{secrets.randbelow(10**self.CODE_LENGTH):0{self.CODE_LENGTH}d}"

    @t.final
    async def _send(self, email: str) -> AuthStep:
        code = self._create_code()
        await self._send_code(email, code)
        return self._ask(email, code)

    @t.final
    def _ask(self, email: str, code: str) -> AuthStep:
        state = AuthEmailState(email=email, digest=self._digest(code))
        return AuthChallenge(
            challenge=AuthEmailChallenge(length=self.CODE_LENGTH), state=state
        )

    @t.final
    def _digest(self, code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()
