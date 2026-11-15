"""What the activity log keeps: a record a change of state, and a query."""

__all__ = ("AuthActivityAction", "AuthActivityQuery", "AuthActivityRecord")

import datetime
import enum
import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from collections.abc import Mapping


class AuthActivityAction(enum.StrEnum):
    """
    What a change of state was: create, update, delete of an entity, or a verb
    of the domain that tells more, kept as its value, so that one more needs
    no migration.
    """

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BIND = "bind"
    UNBIND = "unbind"
    SIGN_IN = "sign_in"
    SIGN_OUT = "sign_out"
    REVOKE = "revoke"
    EXPIRE = "expire"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthActivityRecord:
    """
    A change of state of an entity of the auth, a fact as it was written. Its
    actor, two parts of one whole: ``who``, the uid of the caller, and
    ``session_id``, of its session, none of a caller of none. ``entity_type``
    is the full name of the unit of the entity, ``entity_id`` its id;
    ``context`` what the change was, the attributes the code of its time
    wrote, none for many; ``run_uid`` the uid of the run of operations, of
    the request or of a job.
    """

    who: str
    session_id: str | None
    action: AuthActivityAction
    entity_type: str
    entity_id: str
    context: "Mapping[str, object]"
    run_uid: str
    when: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthActivityQuery:
    """
    What the records found match, each filter optional: of an entity, of an
    actor, of a session, of an action, in a span of time, ``since`` included,
    ``until`` not; the newest first, ``limit`` at most.
    """

    entity_type: str | None = None
    entity_id: str | None = None
    who: str | None = None
    session_id: str | None = None
    action: AuthActivityAction | None = None
    since: datetime.datetime | None = None
    until: datetime.datetime | None = None
    limit: int = 100
