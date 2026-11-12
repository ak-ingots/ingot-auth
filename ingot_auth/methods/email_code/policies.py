"""
The policies of the method of an email and a code: the parameters of a
group and its type.
"""

__all__ = ("AuthEmailSignUpParameters", "AuthEmailSignUpPolicies")

import typing as t
from dataclasses import dataclass, field

from ingots.defaults.operations import BaseOperation
from ingots.puer import Factories


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthEmailSignUpParameters:
    """The email of a sign-up, normalized, its value, not in its ``repr``."""

    value: str = field(repr=False)


AuthEmailSignUpPolicies: t.TypeAlias = Factories[
    BaseOperation[AuthEmailSignUpParameters, t.Any]
]
"""
The group of the policies of the email of a sign-up: the slot of the method
is declared by it, ``AuthEmailSignUpPolicies(AppEmailLength)``.
"""
