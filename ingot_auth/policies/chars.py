"""The policy of the characters."""

__all__ = ("AuthChars", "AuthCharsConfig", "AuthCharsPolicy")

import enum
import typing as t
import unicodedata
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from .errors import AuthPolicyViolationError
from .parameters import AuthHasValue


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


class AuthCharsPolicy(BaseOperation[AuthHasValue, None]):
    """
    A value of the characters allowed by :attr:`CONFIG`, with those required,
    any here: a subclass replaces it.
    """

    # a check of a value the flow running it has given, nothing to require
    PERMISSIONS = Permissions()
    CONFIG: t.ClassVar[AuthCharsConfig] = AuthCharsConfig()

    @t.override
    async def _run(self, parameters: AuthHasValue, metadata: OperationMetadata) -> None:
        config, found = self.CONFIG, AuthChars(0)
        for char in parameters.value:
            chars = AuthChars.of(char)
            found |= chars
            if config.allowed is None or char in config.extra:
                continue
            if not chars or chars not in config.allowed:
                raise AuthPolicyViolationError.for_policy("chars")
        if config.required not in found:
            raise AuthPolicyViolationError.for_policy("chars")
