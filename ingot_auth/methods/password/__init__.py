"""
The password of a profile, one whatever identifier it signs in by, its hash
the secret of the profile: what the methods of a password share, in the slot
``password`` of the methods. A new password is checked by the group of the
policies ``policies_set``, empty unless an application gives policies to it
in a subclass, by whatever method it is set. How it hashes is changed by
subclassing.
"""

__all__ = (
    "AuthHasIdentifiers",
    "AuthPassword",
    "AuthPasswordSetParameters",
    "AuthPasswordSetPolicies",
)

import asyncio
import typing as t
import unicodedata

from ingots.puer import Unit

from ingot_auth.storages import AuthSecretNotFoundError

from .policies import (
    AuthHasIdentifiers,
    AuthPasswordSetParameters,
    AuthPasswordSetPolicies,
)
from .scrypt import hash_password, verify_password

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthPassword(Unit):
    """
    The password of a profile, normalized to NFKC first. A method of a password
    checks a new one by :attr:`policies_set` and keeps its :meth:`hash` as the
    secret of the profile; a sign-in finds the profile by the identifier and
    :meth:`verify` the password against its secret. A profile not found, or
    with no secret, is verified against a hash of nothing all the same, so
    that the time of the refusal tells nothing of it.

    The hash is that of :meth:`_hash`, verified by :meth:`_verify`: scrypt
    with the parameters of OWASP, ``2 ** SCRYPT_LOG_N`` the cost.
    """

    SCRYPT_LOG_N: t.ClassVar[int] = 17
    SCRYPT_R: t.ClassVar[int] = 8
    SCRYPT_P: t.ClassVar[int] = 1

    project: "AuthProject"

    policies_set = AuthPasswordSetPolicies()

    _dummy_secret: str

    @t.final
    def normalize(self, password: str) -> str:
        """A password as it is checked and hashed: in NFKC."""
        return unicodedata.normalize("NFKC", password)

    @t.final
    async def hash(self, password: str) -> str:
        """The hash of a password normalized, the secret of its profile."""
        return await asyncio.to_thread(self._hash, password)

    @t.final
    async def verify(self, password: str, uid: str | None) -> bool:
        """
        Whether a password normalized is that of the profile of a uid; with no
        uid, or no secret of the profile, ``False`` in the same time.
        """
        secret: str | None = None
        if uid is not None:
            try:
                secret = await self.project.auth.storage.profiles.secrets.get(uid)
            except AuthSecretNotFoundError:
                pass
        if secret is None:
            dummy = await asyncio.to_thread(self._get_dummy_secret)
            await asyncio.to_thread(self._verify, password, dummy)
            return False
        return await asyncio.to_thread(self._verify, password, secret)

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
