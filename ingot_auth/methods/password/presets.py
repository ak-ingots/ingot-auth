"""The presets of the policies of the password."""

__all__ = ("AuthPasswordSetPreset",)

from ingot_auth.policies import AuthPolicyPreset

from .contexts import AuthPasswordSetContext


class AuthPasswordSetPreset(AuthPolicyPreset[AuthPasswordSetContext]):
    """The policies of a new password, by whatever method: none here."""
