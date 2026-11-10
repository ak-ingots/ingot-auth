"""What a session keeps, why it closes, and the caller it stands for."""

__all__ = ("AuthCaller", "AuthSessionCloseReason", "AuthSessionRecord")

import datetime
import enum
import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import Caller

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.registry import AuthAttrValue


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


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCaller(Caller):
    """
    A caller signed in: the uid of its profile, the permissions the access
    gives it, and the id of its session, which only the operations of the
    sessions read.
    """

    session_id: str
