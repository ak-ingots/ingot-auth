"""
The metadata: what the consumers of the auth need to read a profile and to
give a sign-up, a sign-in what it asks for, by the subdomains of the auth.
Each is flat lists, linked by ids: a consumer builds what it needs of them.
"""

__all__ = ("AuthMetadata", "AuthProfileMetadata", "AuthSessionMetadata")

from dataclasses import dataclass

from ingot_auth.profile.attrs import AuthAttr
from ingot_auth.profile.tags import AuthTag
from ingot_auth.session.attrs import AuthSessionAttr
from ingot_auth.session.presets import AuthSessionPreset, AuthSessionPresetBinding


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfileMetadata:
    """The registries of the profiles: the ids a profile holds, with their names."""

    tags: tuple[AuthTag, ...]
    attrs: tuple[AuthAttr, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionMetadata:
    """
    What a client gives of a session: the attributes whose source is the
    client, the others are not for it; the presets, and their bindings to
    those attributes.
    """

    attrs: tuple[AuthSessionAttr, ...]
    presets: tuple[AuthSessionPreset, ...]
    bindings: tuple[AuthSessionPresetBinding, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthMetadata:
    """The metadata as a whole, a part a subdomain."""

    profile: AuthProfileMetadata
    session: AuthSessionMetadata
