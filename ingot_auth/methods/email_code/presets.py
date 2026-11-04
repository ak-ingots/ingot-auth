"""The presets of the policies of the method of an email and a code."""

__all__ = ("AuthEmailSignUpPreset",)

from ingot_auth.policies import AuthPolicyPreset

from .contexts import AuthEmailSignUpContext


class AuthEmailSignUpPreset(AuthPolicyPreset[AuthEmailSignUpContext]):
    """The policies of the email of a sign-up: none here."""
