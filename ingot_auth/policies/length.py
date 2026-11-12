"""The policy of the length."""

__all__ = ("AuthLengthConfig", "AuthLengthPolicy")

import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from .errors import AuthPolicyViolationError
from .parameters import AuthHasValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLengthConfig:
    """The length a value takes, in characters: ``max`` of ``None`` is no limit."""

    min: int = 0
    max: int | None = None


class AuthLengthPolicy(BaseOperation[AuthHasValue, None]):
    """
    A value of a length between the limits of :attr:`CONFIG`, both included,
    any here: a subclass replaces it.
    """

    # a check of a value the flow running it has given, nothing to require
    PERMISSIONS = Permissions()
    CONFIG: t.ClassVar[AuthLengthConfig] = AuthLengthConfig()

    @t.override
    async def _run(self, parameters: AuthHasValue, metadata: OperationMetadata) -> None:
        length, config = len(parameters.value), self.CONFIG
        if length < config.min or config.max is not None and length > config.max:
            raise AuthPolicyViolationError.for_policy("length")
