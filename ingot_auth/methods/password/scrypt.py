"""
The hash of a password by scrypt of the standard library, kept as a string
of the PHC format: ``$scrypt$ln=17,r=8,p=1$<salt>$<hash>``, the salt and the
hash in base64 with no padding. The string holds its parameters, so a hash
made with others is still verified.
"""

__all__ = ("hash_password", "verify_password")

import base64
import hashlib
import hmac
import os
import typing as t

SALT_SIZE: t.Final = 16
HASH_SIZE: t.Final = 32


def hash_password(password: str, log_n: int, r: int, p: int) -> str:
    """The hash of a password with a new salt, ``2 ** log_n`` the cost."""
    salt = os.urandom(SALT_SIZE)
    digest = _derive(password, salt, log_n, r, p)
    return f"$scrypt$ln={log_n},r={r},p={p}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, secret: str) -> bool:
    """Whether the password is the one of the hash; ``False`` for no hash."""
    try:
        empty, name, parameters, salt, digest = secret.split("$")
        if empty or name != "scrypt":
            return False
        values = dict(item.split("=") for item in parameters.split(","))
        log_n, r, p = int(values["ln"]), int(values["r"]), int(values["p"])
        expected = _decode(digest)
        derived = _derive(password, _decode(salt), log_n, r, p)
    except ValueError, KeyError:
        return False
    return hmac.compare_digest(derived, expected)


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


def _encode(data: bytes) -> str:
    return base64.b64encode(data).decode().rstrip("=")


def _decode(text: str) -> bytes:
    return base64.b64decode(text + "=" * (-len(text) % 4), validate=True)
