"""The context of an activity, and the parameters of the read of the log."""

__all__ = ("AuthActivityContext", "AuthListActivitiesParameters")

from dataclasses import dataclass

from ingot_auth.storages import AuthActivityQuery


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthActivityContext:
    """
    What a change of state was, optional: a dataclass an activity of a type of
    entity that needs one, its fields the attributes the code of its time
    writes, never a secret, a token, a password, a code. The log keeps it as a
    map of them; a reader assumes none of a type of entity.
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthListActivitiesParameters(AuthActivityQuery):
    """What the activities read match, as :class:`AuthActivityQuery` tells."""
