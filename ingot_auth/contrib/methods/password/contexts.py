"""
The contexts of the presets of the method of a password: each of a step of a
flow, with all the parts the method gives on it, so that a policy taking any
of them binds to its preset with no other context.
"""

__all__ = (
    "AuthHasNickname",
    "AuthNicknameSignUpContext",
    "AuthPasswordSignUpContext",
)

import typing as t

from ingot_auth.policies import AuthValueContext


class AuthHasNickname(t.Protocol):
    """A context with the nickname a password is of, normalized."""

    async def get_nickname(self) -> str: ...


class AuthNicknameSignUpContext(AuthValueContext):
    """The nickname of a sign-up, normalized, its value."""

    __slots__ = ()


class AuthPasswordSignUpContext(AuthValueContext):
    """The password of a sign-up, normalized, its value, and its nickname."""

    __slots__ = ("_nickname",)

    def __init__(self, value: str, nickname: str) -> None:
        super().__init__(value)
        self._nickname = nickname

    async def get_nickname(self) -> str:
        return self._nickname
