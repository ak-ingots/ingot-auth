"""The items of the registries: what tags and attributes are declared with."""

__all__ = ("AuthItem",)

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthItem:
    """
    An item of a registry. ``id`` is what travels and what is stored: given
    explicitly, so it is the same in every environment, and never reused,
    even after its item is deleted. ``name`` is for people: it may change.
    """

    id: int
    name: str
