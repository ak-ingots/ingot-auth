"""The profile: a uid, the sign-up creating it."""

__all__ = ("AuthProfile",)

import datetime
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfile:
    """
    A profile: ``uid`` is what the rest of an application knows the user by.
    The values of its tags and attributes come in another change.
    """

    uid: str
    created_at: datetime.datetime
