"""
The method of a nickname and a password, of one step: an application declares
it as a slot of its methods, ``nickname = Slot(AuthNicknameMethod)``. The
nickname of a sign-up is checked by the preset of the policies of the method,
its slot ``preset_sign_up_nickname``, the password by that of the password of
the profile, ``preset_set`` of :class:`~ingot_auth.methods.password.AuthPassword`,
both empty unless an application binds policies to them in a subclass. The
password is kept as its hash, the secret of the profile. Its flows are
toggled by its configs, :class:`AuthNicknameConfigs`, which the project mixes
into its own.
"""

__all__ = (
    "AuthNicknameConfigs",
    "AuthNicknameMethod",
    "AuthNicknameSignUpContext",
    "AuthNicknameSignUpPreset",
    "AuthNicknameStart",
)

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
from ingot_auth.methods.password import AuthPasswordSetContext
from ingot_auth.storages import AuthIdentityNotFoundError

from .configs import AuthNicknameConfigs
from .contexts import AuthNicknameSignUpContext
from .presets import AuthNicknameSignUpPreset


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthNicknameStart:
    """What a sign-up and a sign-in start with: a nickname and its password."""

    nickname: str
    password: str = field(repr=False)


class AuthNicknameMethod(BaseAuthMethod[AuthNicknameStart, None, None]):
    """
    A nickname and a password. The nickname is normalized first, to NFKC and
    case-folded, so that ``Alice`` is ``alice``: the identifier of the kind
    ``nickname`` is the nickname normalized; the password is normalized by the
    password of the profile. A sign-up checks both by their presets and gives
    the hash of the password as the secret; a sign-in finds the profile by the
    nickname and verifies the password against its secret, a nickname bound
    to none against a hash of nothing all the same.
    """

    IDENTIFIER_KIND: t.ClassVar[str] = "nickname"

    preset_sign_up_nickname = Slot(AuthNicknameSignUpPreset)

    @t.override
    def _get_sign_up_enabled(self) -> bool:
        return self._get_configs().AUTH_SIGN_UP_NICKNAME_ENABLED

    @t.override
    def _get_sign_in_enabled(self) -> bool:
        return self._get_configs().AUTH_SIGN_IN_NICKNAME_ENABLED

    @t.override
    async def _start_sign_up(self, parameters: AuthNicknameStart) -> AuthStep:
        password = self.project.auth.methods.password
        nickname = self._normalize_nickname(parameters.nickname)
        value = password.normalize(parameters.password)
        await self._check(
            "nickname",
            self.preset_sign_up_nickname,
            AuthNicknameSignUpContext(nickname),
        )
        await self._check(
            "password",
            password.preset_set,
            AuthPasswordSetContext(value, (nickname,)),
        )
        return AuthVerified(subject=nickname, secret=await password.hash(value))

    @t.override
    async def _start_sign_in(self, parameters: AuthNicknameStart) -> AuthStep:
        password = self.project.auth.methods.password
        nickname = self._normalize_nickname(parameters.nickname)
        identities = self.project.auth.storage.profiles.identities
        uid: str | None
        try:
            uid = await identities.find_uid(self.IDENTIFIER_KIND, nickname)
        except AuthIdentityNotFoundError:
            uid = None
        if not await password.verify(password.normalize(parameters.password), uid):
            raise AuthMethodRefusedError.create()
        return AuthVerified(subject=nickname)

    def _normalize_nickname(self, nickname: str) -> str:
        return unicodedata.normalize("NFKC", nickname).casefold()

    @t.final
    def _get_configs(self) -> AuthNicknameConfigs:
        # mixed into the configs of the project, as the doc of the package says
        return t.cast(AuthNicknameConfigs, self.project.settings.configs)
