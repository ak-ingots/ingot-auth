"""The attribute of the sessions: a typed value of what a session happened on."""

__all__ = ("AuthSessionAttr", "AuthSessionAttrSource")

import enum
from dataclasses import dataclass

from ingot_auth.registry import AuthAttrType, AuthItem


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
