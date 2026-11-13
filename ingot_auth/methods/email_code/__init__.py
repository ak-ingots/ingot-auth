"""
The method of an email and a code sent to it, of two steps: the start sends
the code, the answer repeats it. An application declares it as a slot of its
methods, ``email_code = Slot(AuthEmailCodeMethod)``: it builds its mail, a
plain text in English, and sends it by the mailer of the auth, in the
background, its operations run by the dispatcher of the auth, so that a
start replies at once. A subclass changes the mail by its hooks. The
email of a sign-up is checked by the group of the policies of the method,
its slot ``policies_sign_up_email``, empty unless an application gives
policies to it in its subclass. Its flows
are toggled by its configs, :class:`AuthEmailCodeConfigs`, which the project
mixes into its own, and are its permissions, :class:`AuthEmailCodePermissions`.
"""

__all__ = (
    "AuthEmailCodeConfigs",
    "AuthEmailCodeMethod",
    "AuthEmailCodePermissions",
    "AuthEmailCodeStart",
    "AuthEmailCodeState",
    "AuthEmailSignUpParameters",
    "AuthEmailSignUpPolicies",
    "AuthSendCodeOperation",
    "AuthSendCodeParameters",
    "AuthSendDenialOperation",
    "AuthSendDenialParameters",
)

import hashlib
import hmac
import secrets
import typing as t
import unicodedata
from dataclasses import dataclass, field

from ingots.defaults.operations import OperationMetadata, Permissions
from ingots.puer import Factory

from ingot_auth.mailers import AuthMail
from ingot_auth.methods import (
    AuthChallenge,
    AuthCodeChallenge,
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)
from ingot_auth.storages import AuthIdentityNotFoundError

from .configs import AuthEmailCodeConfigs
from .operations import (
    AuthSendCodeOperation,
    AuthSendCodeParameters,
    AuthSendDenialOperation,
    AuthSendDenialParameters,
)
from .permissions import AuthEmailCodePermissions
from .policies import AuthEmailSignUpParameters, AuthEmailSignUpPolicies


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailCodeStart:
    """What a sign-up and a sign-in start with: an email."""

    email: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailCodeState:
    """
    What the server keeps till the answer: the email and the digest of the
    code, not the code, for the cache may be read by more than the server.
    """

    email: str
    digest: str = field(repr=False)


class AuthEmailCodeMethod(BaseAuthMethod[AuthEmailCodeStart, str, AuthEmailCodeState]):
    """
    An email and a code of :attr:`CODE_LENGTH` digits sent to it in the
    background, the mail built by :meth:`_build_code_mail`. The email is
    normalized to NFKC and case-folded: the subject is the email normalized.
    The code is good for the attempt, as long as it lives and till the
    answers refused reach their limit.

    A sign-in sends the code only to an email bound to a profile that may
    sign in by the method, and asks for it all the same otherwise, so that
    the answer tells nothing of the email: no code is then good. The email
    of a profile that may not learns it, in place of the code, by the mail
    of :meth:`_build_denial_mail`.
    """

    IDENTIFIER_KIND: t.ClassVar[str] = "email"
    CODE_LENGTH: t.ClassVar[int] = 6

    policies_sign_up_email = AuthEmailSignUpPolicies()

    op_send_code = Factory(AuthSendCodeOperation)
    op_send_denial = Factory(AuthSendDenialOperation)

    @t.override
    def _get_sign_up_enabled(self) -> bool:
        return self._get_configs().AUTH_SIGN_UP_EMAIL_CODE_ENABLED

    @t.override
    def _get_sign_in_enabled(self) -> bool:
        return self._get_configs().AUTH_SIGN_IN_EMAIL_CODE_ENABLED

    @t.override
    def _get_sign_up_permissions(self) -> Permissions:
        return Permissions(AuthEmailCodePermissions.CAN_SIGN_UP)

    @t.override
    def _get_sign_in_permissions(self) -> Permissions:
        return Permissions(AuthEmailCodePermissions.CAN_SIGN_IN)

    @t.override
    async def _start_sign_up(
        self, parameters: AuthEmailCodeStart, metadata: OperationMetadata
    ) -> AuthStep:
        email = self._normalize_email(parameters.email)
        await self._check(
            "email",
            self.policies_sign_up_email,
            AuthEmailSignUpParameters(value=email),
            metadata,
        )
        return await self._send(email, metadata)

    @t.override
    async def _start_sign_in(
        self, parameters: AuthEmailCodeStart, metadata: OperationMetadata
    ) -> AuthStep:
        email = self._normalize_email(parameters.email)
        auth = self.project.auth
        try:
            uid = await auth.storage.profiles.identities.find_uid(
                self.IDENTIFIER_KIND, email
            )
        except AuthIdentityNotFoundError:
            # the same work as for an email bound, so that the time tells
            # nothing of it: the permissions of a uid of nobody
            await auth.access.permissions.get_permissions("")
            return self._ask(email, self._create_code())
        permissions = await auth.access.permissions.get_permissions(uid)
        if not permissions.has(self.get_sign_in_permissions()):
            # told by the mail, not the reply: the client is asked alike
            denial = AuthSendDenialParameters(method=self.get_name(), email=email)
            await auth.dispatcher.dispatch(self.op_send_denial, denial, metadata)
            return self._ask(email, self._create_code())
        return await self._send(email, metadata)

    @t.override
    async def _answer(self, state: AuthEmailCodeState, answer: str) -> AuthStep:
        if not hmac.compare_digest(self._digest(answer), state.digest):
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=state.email)

    def _build_code_mail(self, email: str, code: str) -> AuthMail:
        """
        The mail of a code: a plain text in English here, the code in the text
        only, as the subject is in the ``repr`` of the mail.
        """
        return AuthMail(
            to=email,
            subject="Your code",
            text=(
                f"Your code is {code}.\n\n"
                "Type it where you asked for it. If you did not, ignore this "
                "mail: nobody gets in without the code.\n"
            ),
        )

    def _build_denial_mail(self, email: str) -> AuthMail:
        """
        The mail telling the sign-in by the method is closed to the profile of
        the email: a plain text in English here.
        """
        return AuthMail(
            to=email,
            subject="The sign-in by email is closed to you",
            text=(
                "Someone asked to sign in by this email, and the sign-in by "
                "email is closed to your account: no code was sent. Ask the "
                "support to open it.\n"
            ),
        )

    def _normalize_email(self, email: str) -> str:
        return unicodedata.normalize("NFKC", email).strip().casefold()

    def _create_code(self) -> str:
        """A code of random digits."""
        return f"{secrets.randbelow(10**self.CODE_LENGTH):0{self.CODE_LENGTH}d}"

    @t.final
    def _get_configs(self) -> AuthEmailCodeConfigs:
        # mixed into the configs of the project, as the doc of the package says
        return t.cast(AuthEmailCodeConfigs, self.project.settings.configs)

    @t.final
    async def _send(self, email: str, metadata: OperationMetadata) -> AuthStep:
        code = self._create_code()
        sending = AuthSendCodeParameters(method=self.get_name(), email=email, code=code)
        await self.project.auth.dispatcher.dispatch(
            self.op_send_code, sending, metadata
        )
        return self._ask(email, code)

    @t.final
    def _ask(self, email: str, code: str) -> AuthStep:
        state = AuthEmailCodeState(email=email, digest=self._digest(code))
        return AuthChallenge(
            challenge=AuthCodeChallenge(length=self.CODE_LENGTH), state=state
        )

    @t.final
    def _digest(self, code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()
