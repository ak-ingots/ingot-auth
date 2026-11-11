"""
What the storage of the sessions keeps: the sessions and why they close, and
the items of the registries of their attributes and presets.
"""

__all__ = (
    "AuthSessionAttr",
    "AuthSessionAttrSource",
    "AuthSessionCloseReason",
    "AuthSessionPreset",
    "AuthSessionPresetBinding",
    "AuthSessionRecord",
)

import datetime
import enum
import typing as t
from dataclasses import dataclass

from ..items import AuthAttrType, AuthItem

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ..items import AuthAttrValue


class AuthSessionCloseReason(enum.StrEnum):
    """Why a session closed."""

    SIGNED_OUT = "signed_out"
    REVOKED = "revoked"
    EVICTED = "evicted"
    EXPIRED_IDLE = "expired_idle"
    EXPIRED_ABSOLUTE = "expired_absolute"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionRecord:
    """
    A session, open or closed, the record of a sign-in: ``id`` is public, and
    never authenticates; ``token_hash`` is the sha256 of the token, which the
    server never keeps. ``values`` are those of the attributes of the session,
    by their ids. A closed one has the time and the reason it closed at.
    """

    id: str
    uid: str
    method: str
    token_hash: str
    values: "Mapping[int, AuthAttrValue]"
    opened_at: datetime.datetime
    closed_at: datetime.datetime | None = None
    close_reason: AuthSessionCloseReason | None = None


class AuthSessionAttrSource(enum.StrEnum):
    """
    Who gives the values of an attribute, and so how far they are trusted:
    the transport, from the call itself (the IP), and a client never gives
    them; the client (its device, its version), what it says, not a fact; the
    provider of the method of the sign-in, once its token is checked; the
    server, deriving them from the others (the country by the IP).
    """

    TRANSPORT = "transport"
    CLIENT = "client"
    PROVIDER = "provider"
    DERIVED = "derived"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionAttr(AuthItem):
    """
    An attribute of the sessions: ``ip``, ``device/model``. Its type and its
    source are given once: renaming keeps them, and nothing changes them.
    """

    type: AuthAttrType
    source: AuthSessionAttrSource


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
