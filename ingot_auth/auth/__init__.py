"""The auth unit: the sign-up, the sign-in and the sessions of the project."""

__all__ = ("AuthUnit",)

from ingots.puer import Unit


class AuthUnit(Unit):
    """
    The auth of the project. Empty for now: the sign-up, the sign-in, the
    profiles and the sessions come as its slots.
    """
