"""
The policies of the method of a nickname and a password: the parameters of
a group, of a step of a flow, with all the parts the method gives on it, so
that a policy taking any of them joins the group, and the type of the group.
The password has its own, of the password of the profile.
"""

__all__ = ("AuthNicknameSignUpParameters", "AuthNicknameSignUpPolicies")

import typing as t
from dataclasses import dataclass, field

from ingots.defaults.operations import BaseOperation
from ingots.puer import Factories


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthNicknameSignUpParameters:
    """The nickname of a sign-up, normalized, its value, not in its ``repr``."""

    value: str = field(repr=False)


AuthNicknameSignUpPolicies: t.TypeAlias = Factories[
    BaseOperation[AuthNicknameSignUpParameters, t.Any]
]
"""
The group of the policies of the nickname of a sign-up: the slot of the
method is declared by it, ``AuthNicknameSignUpPolicies(AppNicknameLength)``.
"""
