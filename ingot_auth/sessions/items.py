"""What opening a session gives, what a user sees of its own."""

__all__ = (
    "AuthListSessionsParameters",
    "AuthOwnSession",
    "AuthRevokeOwnSessionParameters",
    "AuthSessionExpired",
    "AuthSessionInfo",
    "AuthSessionToken",
)

import datetime
import typing as t
from dataclasses import dataclass, field

from ingot_auth.activities import AuthActivityContext

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue, AuthSessionCloseReason


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionToken:
    """
    The token of a session just opened, given once, kept by none but the
    client and never in a ``repr``, and the uid of its session, public.
    """

    session_uid: str
    token: str = field(repr=False)


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthOwnSession:
    """
    An open session as its user sees it: its public uid, never its token, the
    values of its attributes by their ids, the device, the place, the times
    it opened and was seen at, and whether it is the current one, that of the
    caller.
    """

    uid: str
    attr_values: "Mapping[int, AuthAttrValue]"
    opened_at: datetime.datetime
    seen_at: datetime.datetime
    is_current: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRevokeOwnSessionParameters:
    """The public uid of a session of the caller's own."""

    session_uid: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthListSessionsParameters:
    """The uid of a profile; its closed sessions too, the record, if told."""

    profile_uid: str
    closed: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionInfo:
    """
    A session of a profile as an operator sees it, open or closed, the record
    of a sign-in: never its token nor its hash. A closed one tells when and
    why; by whom, the activity log tells, by the uid of the session.
    """

    uid: str
    profile_uid: str
    method: str
    attr_values: "Mapping[int, AuthAttrValue]"
    opened_at: datetime.datetime
    seen_at: datetime.datetime
    closed_at: datetime.datetime | None
    close_reason: "AuthSessionCloseReason | None"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionExpired(AuthActivityContext):
    """The context of a session expiring in the activity log: why it closed."""

    reason: str
