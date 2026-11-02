"""The contexts of the presets of the method of an email."""

__all__ = ("AuthEmailSignUpContext",)

from ingot_auth.policies import AuthValueContext


class AuthEmailSignUpContext(AuthValueContext):
    """The email of a sign-up, normalized, its value."""

    __slots__ = ()
