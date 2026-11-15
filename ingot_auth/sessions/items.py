"""What opening a session gives, what a user sees of its own."""

__all__ = ("AuthOwnSession", "AuthRevokeOwnSessionParameters", "AuthSessionToken")

import datetime
import typing as t
from dataclasses import dataclass, field

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionToken:
    """
    The token of a session just opened, given once, kept by none but the
    client and never in a ``repr``, and the id of its session, public.
    """

    session_id: str
    token: str = field(repr=False)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthOwnSession:
    """
    An open session as its user sees it: its public id, never its token, the
    values of its attributes by their ids, the device, the place, the times
    it opened and was seen at, and whether it is the current one, that of the
    caller.
    """

    id: str
    attr_values: "Mapping[int, AuthAttrValue]"
    opened_at: datetime.datetime
    seen_at: datetime.datetime
    is_current: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRevokeOwnSessionParameters:
    """The public id of a session of the caller's own."""

    session_id: str
