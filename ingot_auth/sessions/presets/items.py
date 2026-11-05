"""The preset: a set of the attributes of the sessions, bound to it."""

__all__ = ("AuthSessionPreset", "AuthSessionPresetBinding")

from dataclasses import dataclass

from ingot_auth.registry import AuthItem


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionPreset(AuthItem):
    """
    A preset of the sessions: ``sign_in``, ``sign_up/apple``. What it asks
    for are its bindings, a preset holds only its id and its name.
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionPresetBinding:
    """
    An attribute of the sessions bound to a preset: a preset may have many,
    an attribute be in many. ``required`` tells whether the preset needs a
    value of it or only takes one.
    """

    preset_id: int
    attr_id: int
    required: bool
