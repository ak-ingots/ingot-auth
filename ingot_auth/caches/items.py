"""
What the caches keep of their own: the attempts, and the callers of the
sessions.
"""

__all__ = ("AuthAttempt", "AuthCaller")

import datetime
import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import Caller

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthAttempt:
    """
    A flow waiting for an answer, a sign-up, a sign-in between its steps:
    ``id`` is what the client holds, random, the rest stays with the server.
    ``values`` are those of the attributes of the session the client started
    with; ``failures`` the answers refused so far.
    """

    id: str
    flow: str
    method: str
    state: object
    values: "Mapping[int, AuthAttrValue]"
    expires_at: datetime.datetime
    failures: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCaller(Caller):
    """
    A caller signed in: the uid of its profile, the permissions the access
    gives it, and the id of its session, which only the operations of the
    sessions read.
    """

    session_id: str
