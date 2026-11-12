"""
The policies of the password: the parameters of a group, of a point of a
flow, with all the parts there are at it, so that a policy taking any of
them joins the group, and the type of the group.
"""

__all__ = ("AuthHasIdentifiers", "AuthPasswordSetParameters", "AuthPasswordSetPolicies")

import typing as t
from dataclasses import dataclass, field

from ingots.defaults.operations import BaseOperation
from ingots.puer import Factories


class AuthHasIdentifiers(t.Protocol):
    """Parameters with the identifiers of the profile a password is of."""

    @property
    def identifiers(self) -> tuple[str, ...]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthPasswordSetParameters:
    """
    A new password given, normalized, its value, with the identifiers of its
    profile, normalized too, so that a policy refuses a password that is one:
    neither in its ``repr``.
    """

    value: str = field(repr=False)
    identifiers: tuple[str, ...] = field(repr=False)


AuthPasswordSetPolicies: t.TypeAlias = Factories[
    BaseOperation[AuthPasswordSetParameters, t.Any]
]
"""
The group of the policies of a new password, by whatever method: the slot of
the password is declared by it, ``AuthPasswordSetPolicies(AppPasswordLength)``.
"""
