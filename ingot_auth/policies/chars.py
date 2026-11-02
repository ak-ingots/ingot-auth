"""The policy of the characters."""

__all__ = ("AuthChars", "AuthCharsConfig", "AuthCharsPolicy")

import enum
import typing as t
import unicodedata
from dataclasses import dataclass

from .base import BaseAuthPolicy
from .contexts import AuthHasValue


class AuthChars(enum.Flag):
    """
    The sets of characters, by the categories of Unicode: ``LETTERS`` of any
    script (``L*``), ``DIGITS`` decimal ones (``Nd``), ``SYMBOLS`` the
    punctuation and the symbols (``P*``, ``S*``), ``SPACES`` the separators of
    words (``Zs``). A character of none of them, a control one, is in none.
    """

    LETTERS = enum.auto()
    DIGITS = enum.auto()
    SYMBOLS = enum.auto()
    SPACES = enum.auto()

    @classmethod
    def of(cls, char: str) -> "AuthChars":
        """The set a character is in, an empty one if none."""
        category = unicodedata.category(char)
        if category.startswith("L"):
            return cls.LETTERS
        if category == "Nd":
            return cls.DIGITS
        if category[0] in "PS":
            return cls.SYMBOLS
        if category == "Zs":
            return cls.SPACES
        return cls(0)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCharsConfig:
    """
    The characters a value takes: each of the sets ``allowed`` or one of
    ``extra``, and one at least of each set ``required``. ``allowed`` of
    ``None`` takes any.
    """

    allowed: AuthChars | None = None
    extra: str = ""
    required: AuthChars = AuthChars(0)


class AuthCharsPolicy(BaseAuthPolicy[AuthHasValue, AuthCharsConfig]):
    """A value of the characters allowed, with those required."""

    @t.override
    async def _accepts(self, context: AuthHasValue, config: AuthCharsConfig) -> bool:
        found = AuthChars(0)
        for char in await context.get_value():
            chars = AuthChars.of(char)
            found |= chars
            if config.allowed is None or char in config.extra:
                continue
            if not chars or chars not in config.allowed:
                return False
        return config.required in found
