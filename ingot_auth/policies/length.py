"""The policy of the length."""

__all__ = ("AuthLengthConfig", "AuthLengthPolicy")

import typing as t
from dataclasses import dataclass

from .base import BaseAuthPolicy
from .contexts import AuthHasValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLengthConfig:
    """The length a value takes, in characters: ``max`` of ``None`` is no limit."""

    min: int = 0
    max: int | None = None


class AuthLengthPolicy(BaseAuthPolicy[AuthHasValue, AuthLengthConfig]):
    """A value of a length between the limits, both included."""

    @t.override
    async def _accepts(self, context: AuthHasValue, config: AuthLengthConfig) -> bool:
        value = await context.get_value()
        if len(value) < config.min:
            return False
        return config.max is None or len(value) <= config.max
