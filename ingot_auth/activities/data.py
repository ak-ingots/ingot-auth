"""The context of an activity."""

__all__ = ("AuthActivityContext",)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthActivityContext:
    """
    What a change of state was, optional: a dataclass an activity of a type of
    entity that needs one, its fields the attributes the code of its time
    writes, never a secret, a token, a password, a code. The log keeps it as a
    map of them; a reader assumes none of a type of entity.
    """
