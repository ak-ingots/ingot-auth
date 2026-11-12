"""The errors of the policies."""

__all__ = ("AuthPolicyViolationError",)

import typing as t


class AuthPolicyViolationError(Exception):
    """
    A value breaks a policy. ``args`` are the message and the name of the
    policy, not the value, a password, say.
    """

    @classmethod
    def for_policy(cls, policy: str) -> t.Self:
        return cls(f"the value breaks the policy {policy!r}", policy)

    @property
    def policy(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
