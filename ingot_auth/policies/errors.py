"""The errors of the policies."""

__all__ = (
    "AuthPolicyNotFoundError",
    "AuthPolicyViolationError",
)

import typing as t


class AuthPolicyNotFoundError(Exception):
    """
    No slot holds a policy of the class. ``args`` are the message and the
    qualified name of the class.
    """

    @classmethod
    def for_kind(cls, kind: type) -> t.Self:
        name = f"{kind.__module__}.{kind.__qualname__}"
        return cls(f"no policy of {name}", name)

    @property
    def kind(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


class AuthPolicyViolationError(Exception):
    """
    A value breaks a policy of a preset. ``args`` are the message and the
    name of the binding, not the value, a password, say.
    """

    @classmethod
    def for_binding(cls, binding: str) -> t.Self:
        return cls(f"the value breaks the policy of {binding!r}", binding)

    @property
    def binding(self) -> str:
        return t.cast(str, self.args[1])

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])
