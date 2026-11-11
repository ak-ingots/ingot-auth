"""The presets of the policies of the method of a nickname and a password."""

__all__ = ("AuthNicknameSignUpPreset",)

from ingot_auth.policies import AuthPolicyPreset

from .contexts import AuthNicknameSignUpContext


class AuthNicknameSignUpPreset(AuthPolicyPreset[AuthNicknameSignUpContext]):
    """The policies of the nickname of a sign-up: none here."""
