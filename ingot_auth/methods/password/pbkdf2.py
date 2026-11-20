"""
The hash of a password by PBKDF2 with HMAC-SHA256 of the standard library,
kept as a string of the PHC format: ``$pbkdf2-sha256$i=600000$<salt>$<hash>``.
The string holds its iterations, so a hash made with others is still
verified.
"""

__all__ = ("AuthPbkdf2PasswordHasher",)

import hashlib
import hmac
import os
import typing as t

from .hashers import BaseAuthPasswordHasher
from .phc import decode, encode, parse_parameters

SALT_SIZE: t.Final = 16
HASH_SIZE: t.Final = 32


class AuthPbkdf2PasswordHasher(BaseAuthPasswordHasher):
    """
    PBKDF2 with HMAC-SHA256 of ``ITERATIONS``, the 600 000 of OWASP: no
    memory dear, so cheap on a GPU, but approved by FIPS, for where FIPS is
    required.
    """

    NAME = "pbkdf2-sha256"
    ITERATIONS: t.ClassVar[int] = 600_000

    @t.override
    def hash(self, password: str) -> str:
        salt = os.urandom(SALT_SIZE)
        digest = _derive(password, salt, self.ITERATIONS)
        return f"{self._get_prefix()}{encode(salt)}${encode(digest)}"

    @t.override
    def verify(self, password: str, secret: str) -> bool:
        try:
            empty, name, parameters, salt, digest = secret.split("$")
            if empty or name != self.NAME:
                return False
            iterations = parse_parameters(parameters)["i"]
            expected = decode(digest)
            derived = _derive(password, decode(salt), iterations)
        except ValueError, KeyError:
            return False
        return hmac.compare_digest(derived, expected)

    @t.override
    def needs_rehash(self, secret: str) -> bool:
        return not secret.startswith(self._get_prefix())

    @t.final
    def _get_prefix(self) -> str:
        return f"${self.NAME}$i={self.ITERATIONS}$"


def _derive(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, iterations, dklen=HASH_SIZE
    )
