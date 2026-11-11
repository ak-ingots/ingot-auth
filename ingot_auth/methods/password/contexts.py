"""
The contexts of the presets of the password: each of a point of a flow, with
all the parts there are at it, so that a policy taking any of them binds to
its preset with no other context.
"""

__all__ = ("AuthHasIdentifiers", "AuthPasswordSetContext")

import typing as t

from ingot_auth.policies import AuthValueContext


class AuthHasIdentifiers(t.Protocol):
    """A context with the identifiers of the profile a password is of."""

    async def get_identifiers(self) -> tuple[str, ...]: ...


class AuthPasswordSetContext(AuthValueContext):
    """
    A new password given, normalized, its value, with the identifiers of its
    profile, normalized too, so that a policy refuses a password that is one.
    """

    __slots__ = ("_identifiers",)

    def __init__(self, value: str, identifiers: tuple[str, ...]) -> None:
        super().__init__(value)
        self._identifiers = identifiers

    async def get_identifiers(self) -> tuple[str, ...]:
        return self._identifiers
