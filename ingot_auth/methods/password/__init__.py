"""
The password of a profile, one whatever identifier it signs in by, its hash
the secret of the profile: what the methods of a password share, in the slot
``password`` of the methods. A new password is checked by the group of the
policies ``policies_set``, the length of OWASP alone unless an application
gives its own in a subclass, by whatever method it is set. It is hashed by the hasher of
its slot ``hasher_default`` and verified by the one of its slots
``hasher_*`` whose algorithm the hash names.
"""

__all__ = (
    "AuthHasIdentifiers",
    "AuthPassword",
    "AuthPasswordLengthPolicy",
    "AuthPasswordSetParameters",
    "AuthPasswordSetPolicies",
    "AuthPbkdf2PasswordHasher",
    "AuthScryptPasswordHasher",
    "BaseAuthPasswordHasher",
)

import asyncio
import typing as t
import unicodedata

from ingots.puer import Slot, Unit

from ingot_auth.storages import AuthSecretNotFoundError

from .policies import (
    AuthHasIdentifiers,
    AuthPasswordLengthPolicy,
    AuthPasswordSetParameters,
    AuthPasswordSetPolicies,
)
from .hashers import BaseAuthPasswordHasher
from .pbkdf2 import AuthPbkdf2PasswordHasher
from .phc import get_name
from .scrypt import AuthScryptPasswordHasher

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

    A password is hashed by the hasher of the slot ``hasher_default``, none
    by default, as every strategy, and verified by the hasher of the slots
    ``hasher_*`` whose :attr:`~BaseAuthPasswordHasher.NAME` the hash names,
    those of the standard library here, ``hasher_scrypt`` and
    ``hasher_pbkdf2``: another default, or another cost, keeps the passwords
    set before, and a password verified by a hash the default would not make
    is hashed again by it, as OWASP upgrades a work factor. A hasher of
    another library comes in a slot of its own.
    """

    project: "AuthProject"
    hasher_default = Slot(BaseAuthPasswordHasher)  # type: ignore[type-abstract]
    hasher_scrypt = Slot(AuthScryptPasswordHasher)
    hasher_pbkdf2 = Slot(AuthPbkdf2PasswordHasher)

    policies_set = AuthPasswordSetPolicies(AuthPasswordLengthPolicy)

    _dummy_secret: str
    _hashers: dict[str, BaseAuthPasswordHasher]

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
        if secret is None or uid is None:
            dummy = await asyncio.to_thread(self._get_dummy_secret)
            await asyncio.to_thread(self._verify, password, dummy)
            return False
        if not await asyncio.to_thread(self._verify, password, secret):
            return False
        if self.hasher_default.needs_rehash(secret):
            # the default of today and its cost, as OWASP upgrades a work factor
            secret = await self.hash(password)
            await self.project.auth.storage.profiles.secrets.put(uid, secret)
        return True

    def _hash(self, password: str) -> str:
        """The hash of a password by the default hasher, run in a thread."""
        return self.hasher_default.hash(password)

    def _verify(self, password: str, secret: str) -> bool:
        """
        Whether a password is that of a hash, by the hasher of its algorithm;
        ``False`` for a hash of none of them. Run in a thread.
        """
        hasher = self._get_hashers().get(get_name(secret))
        return hasher is not None and hasher.verify(password, secret)

    @t.final
    def _get_hashers(self) -> dict[str, BaseAuthPasswordHasher]:
        """The hashers of the slots ``hasher_*`` by their names, the default first."""
        try:
            return self._hashers
        except AttributeError:
            pass
        hashers: dict[str, BaseAuthPasswordHasher] = {}
        kind = BaseAuthPasswordHasher
        for name, _ in type(self).slots_iter(kind):  # type: ignore[type-abstract]
            hasher = self.slots_find_entity(name, kind)  # type: ignore[type-abstract]
            hashers.setdefault(hasher.NAME, hasher)
        self._hashers = hashers
        return self._hashers

    @t.final
    def _get_dummy_secret(self) -> str:
        try:
            return self._dummy_secret
        except AttributeError:
            pass
        self._dummy_secret = self._hash("")
        return self._dummy_secret
