"""
The contexts of the presets of the method of a nickname and a password:
each of a step of a flow, with all the parts the method gives on it, so that
a policy taking any of them binds to its preset with no other context. The
password has its own, of the password of the profile.
"""

__all__ = ("AuthNicknameSignUpContext",)

from ingot_auth.policies import AuthValueContext


class AuthNicknameSignUpContext(AuthValueContext):
    """The nickname of a sign-up, normalized, its value."""

    __slots__ = ()
