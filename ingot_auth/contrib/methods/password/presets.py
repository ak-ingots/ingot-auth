"""The presets of the policies of the method of a password."""

__all__ = ("AuthNicknameSignUpPreset", "AuthPasswordSignUpPreset")

from ingot_auth.policies import AuthPolicyPreset

from .contexts import AuthNicknameSignUpContext, AuthPasswordSignUpContext


class AuthNicknameSignUpPreset(AuthPolicyPreset[AuthNicknameSignUpContext]):
    """The policies of the nickname of a sign-up: none here."""


class AuthPasswordSignUpPreset(AuthPolicyPreset[AuthPasswordSignUpContext]):
    """The policies of the password of a sign-up: none here."""
