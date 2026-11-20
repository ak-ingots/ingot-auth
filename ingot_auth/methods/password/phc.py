"""
The strings of the PHC format a hash of a password is kept as:
``$<name>$<parameters>$<salt>$<hash>``, the salt and the hash in base64 with
no padding; the name tells the algorithm, the parameters its cost.
"""

__all__ = ("decode", "encode", "get_name", "parse_parameters")

import base64


def get_name(secret: str) -> str:
    """The name of the algorithm of a hash; empty for what is no hash."""
    empty, _, rest = secret.partition("$")
    return "" if empty else rest.partition("$")[0]


def parse_parameters(parameters: str) -> dict[str, int]:
    """
    The parameters of a hash, ``ln=17,r=8,p=1``, by their names.

    :raises ValueError: a parameter that is not ``name=<int>``.
    """
    values = {}
    for item in parameters.split(","):
        name, separator, value = item.partition("=")
        if not separator:
            raise ValueError(item)
        values[name] = int(value)
    return values


def encode(data: bytes) -> str:
    """Bytes in base64 with no padding."""
    return base64.b64encode(data).decode().rstrip("=")


def decode(text: str) -> bytes:
    """
    Bytes of base64 with no padding.

    :raises ValueError: what is not base64.
    """
    return base64.b64decode(text + "=" * (-len(text) % 4), validate=True)
