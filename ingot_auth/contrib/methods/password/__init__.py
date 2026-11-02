"""
The method of a nickname and a password, of one step: an application declares
it as a slot of its methods, ``password = Slot(AuthPasswordMethod)``. The
nickname and the password of a sign-up are checked by the presets of the
policies of the method, its slots ``preset_sign_up_nickname`` and
``preset_sign_up_password``, empty unless an application binds policies to
them in a subclass of the method. The password is kept as its
hash, a secret of the nickname, by scrypt of the standard library; how it
hashes is changed by subclassing.
"""

__all__ = (
    "AuthHasNickname",
    "AuthNicknameSignUpContext",
    "AuthNicknameSignUpPreset",
    "AuthPasswordMethod",
    "AuthPasswordSignUpContext",
    "AuthPasswordSignUpPreset",
    "AuthPasswordStart",
)

import asyncio
import typing as t
import unicodedata
from dataclasses import dataclass, field

from ingots.puer import Slot

from ingot_auth.methods import (
    AuthMethodRefusedError,
    AuthStep,
    AuthVerified,
    BaseAuthMethod,
)
from ingot_auth.profile.secrets import AuthSecretNotFoundError

from .contexts import (
    AuthHasNickname,
    AuthNicknameSignUpContext,
    AuthPasswordSignUpContext,
)
from .presets import AuthNicknameSignUpPreset, AuthPasswordSignUpPreset
from .scrypt import hash_password, verify_password


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthPasswordStart:
    """What a sign-up and a sign-in start with: a nickname and its password."""

    nickname: str
    password: str = field(repr=False)


class AuthPasswordMethod(BaseAuthMethod[AuthPasswordStart, None, None]):
    """
    A nickname and a password. Both are normalized first, to NFKC, the
    nickname to its case-folded form too, so that ``Alice`` is ``alice``: the
    subject is the nickname normalized. A sign-up checks them by their
    presets of the policies and gives the hash of the password as the
    secret; a sign-in verifies the password against it. A nickname with no secret is
    verified against a hash of nothing all the same, so that the time of the
    refusal tells nothing of it.

    The hash is that of :meth:`_hash`, verified by :meth:`_verify`: scrypt
    with the parameters of OWASP, ``2 ** SCRYPT_LOG_N`` the cost.
    """

    SCRYPT_LOG_N: t.ClassVar[int] = 17
    SCRYPT_R: t.ClassVar[int] = 8
    SCRYPT_P: t.ClassVar[int] = 1

    preset_sign_up_nickname = Slot(AuthNicknameSignUpPreset)
    preset_sign_up_password = Slot(AuthPasswordSignUpPreset)

    _dummy_secret: str

    @t.override
    async def _start_sign_up(self, parameters: AuthPasswordStart) -> AuthStep:
        nickname = self._normalize_nickname(parameters.nickname)
        password = self._normalize_password(parameters.password)
        await self._check(
            "nickname",
            self.preset_sign_up_nickname,
            AuthNicknameSignUpContext(nickname),
        )
        await self._check(
            "password",
            self.preset_sign_up_password,
            AuthPasswordSignUpContext(password, nickname),
        )
        secret = await asyncio.to_thread(self._hash, password)
        return AuthVerified(subject=nickname, secret=secret)

    @t.override
    async def _start_sign_in(self, parameters: AuthPasswordStart) -> AuthStep:
        nickname = self._normalize_nickname(parameters.nickname)
        password = self._normalize_password(parameters.password)
        secrets = self.project.auth.storage.profile.secrets
        try:
            secret = await secrets.get(self.get_name(), nickname)
        except AuthSecretNotFoundError:
            dummy = await asyncio.to_thread(self._get_dummy_secret)
            await asyncio.to_thread(self._verify, password, dummy)
            raise AuthMethodRefusedError.create() from None
        if not await asyncio.to_thread(self._verify, password, secret):
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=nickname)

    def _normalize_nickname(self, nickname: str) -> str:
        return unicodedata.normalize("NFKC", nickname).casefold()

    def _normalize_password(self, password: str) -> str:
        return unicodedata.normalize("NFKC", password)

    def _hash(self, password: str) -> str:
        """The hash of a password, run in a thread."""
        return hash_password(password, self.SCRYPT_LOG_N, self.SCRYPT_R, self.SCRYPT_P)

    def _verify(self, password: str, secret: str) -> bool:
        """Whether a password is that of a hash :meth:`_hash` made, in a thread."""
        return verify_password(password, secret)

    @t.final
    def _get_dummy_secret(self) -> str:
        try:
            return self._dummy_secret
        except AttributeError:
            pass
        self._dummy_secret = self._hash("")
        return self._dummy_secret
