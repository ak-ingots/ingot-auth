"""The tag: a mark on a profile."""

__all__ = ("AuthTag",)

from dataclasses import dataclass

from ingot_auth.registry import AuthItem


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthTag(AuthItem):
    """
    A tag of the profiles: ``beta``, ``staff``. A mark, not a permission:
    the permissions of a caller decide what it may do.
    """
