"""The errors of the secrets."""

__all__ = ("AuthSecretNotFoundError",)

import typing as t

from ingot_auth.profiles.identities.errors import AuthIdentityError


class AuthSecretNotFoundError(AuthIdentityError):
    """The subject has no secret of the method."""

    @classmethod
    def for_method(cls, method: str) -> t.Self:
        return cls(f"{method}: the subject has no secret", method)
