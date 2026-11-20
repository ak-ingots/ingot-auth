"""
The hash of a password by scrypt of the standard library, kept as a string
of the PHC format: ``$scrypt$ln=17,r=8,p=1$<salt>$<hash>``. The string holds
its parameters, so a hash made with others is still verified.
"""

__all__ = ("AuthScryptPasswordHasher",)

import hashlib
import hmac
import os
import typing as t

from .hashers import BaseAuthPasswordHasher
from .phc import decode, encode, parse_parameters

SALT_SIZE: t.Final = 16
HASH_SIZE: t.Final = 32


class AuthScryptPasswordHasher(BaseAuthPasswordHasher):
    """
    scrypt of ``2 ** SCRYPT_LOG_N``, ``SCRYPT_R`` and ``SCRYPT_P``, the
    highest of OWASP: 128 MiB a hash, memory-hard, so dear on a GPU too. A
    subclass takes another cost, one of a like defence by OWASP measured on
    its servers.
    """

    NAME = "scrypt"
    SCRYPT_LOG_N: t.ClassVar[int] = 17
    SCRYPT_R: t.ClassVar[int] = 8
    SCRYPT_P: t.ClassVar[int] = 1

    @t.override
    def hash(self, password: str) -> str:
        salt = os.urandom(SALT_SIZE)
        digest = _derive(
            password, salt, self.SCRYPT_LOG_N, self.SCRYPT_R, self.SCRYPT_P
        )
        return f"{self._get_prefix()}{encode(salt)}${encode(digest)}"

    @t.override
    def verify(self, password: str, secret: str) -> bool:
        try:
            empty, name, parameters, salt, digest = secret.split("$")
            if empty or name != self.NAME:
                return False
            values = parse_parameters(parameters)
            log_n, r, p = values["ln"], values["r"], values["p"]
            expected = decode(digest)
            derived = _derive(password, decode(salt), log_n, r, p)
        except ValueError, KeyError:
            return False
        return hmac.compare_digest(derived, expected)

    @t.override
    def needs_rehash(self, secret: str) -> bool:
        return not secret.startswith(self._get_prefix())

    @t.final
    def _get_prefix(self) -> str:
        return (
            f"${self.NAME}$ln={self.SCRYPT_LOG_N},r={self.SCRYPT_R},p={self.SCRYPT_P}$"
        )


def _derive(password: str, salt: bytes, log_n: int, r: int, p: int) -> bytes:
    n = 2**log_n
    return hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=n,
        r=r,
        p=p,
        # what scrypt takes, 128 bytes by n and r, twice over
        maxmem=256 * n * r * p,
        dklen=HASH_SIZE,
    )
