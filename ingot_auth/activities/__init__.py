"""
The activity log of the auth, by ADR 0015: a record a change of state of an
entity, written by its operation in its transaction, read by the auditors.
An operation records its change, an action, with a context if it needs one::

    await self.project.auth.activities.record(
        self.parent, str(tag.id), AuthActivityAction.CREATE, metadata
    )

The actor is the caller of the metadata and its session; the server doing a
thing by itself acts as :data:`AUTH_SYSTEM`, in a run of its own.
"""

__all__ = (
    "AUTH_SYSTEM",
    "AuthActivitiesAuditorsGroup",
    "AuthActivitiesPermissions",
    "AuthActivitiesUnit",
    "AuthActivityContext",
    "AuthListActivitiesCommand",
    "AuthListActivitiesOperation",
    "AuthListActivitiesParameters",
    "AuthStrictActivityFailure",
    "AuthSwallowActivityFailure",
    "BaseAuthActivityFailure",
)

import dataclasses
import datetime
import typing as t

from ingots.defaults.operations import (
    Caller,
    OperationMetadata,
    OperationsOwner,
    PermissionsSlot,
)
from ingots.puer import Entity, Factory, Slot
from ingots.puer.cli import CliUnit

from ingot_auth.access.groups import AuthGroupsOwner
from ingot_auth.caches import AuthCaller
from ingot_auth.storages import AuthActivityAction, AuthActivityRecord

from .commands import AuthListActivitiesCommand
from .failures import (
    AuthStrictActivityFailure,
    AuthSwallowActivityFailure,
    BaseAuthActivityFailure,
)
from .groups import AuthActivitiesAuditorsGroup
from .items import AuthActivityContext, AuthListActivitiesParameters
from .operations import AuthListActivitiesOperation
from .permissions import AuthActivitiesPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject

# the caller of what the server does by itself, a session expiring: not the
# initiative of a user, nor of an operator
AUTH_SYSTEM: t.Final = Caller(uid="system")


class AuthActivitiesUnit(AuthGroupsOwner, OperationsOwner, CliUnit):
    """
    The activity log: :meth:`record`, which the operations of the auth call,
    the strategy of a failure to write it in the slot ``failure``, none by
    default, which the project declares, and the read of it by the auditors,
    ``auth.activities.grp_auditors``.
    """

    cli_name = "activities"
    cli_description = "The activity log: every change of state of the auth."

    project: "AuthProject"

    grp_auditors = Slot(AuthActivitiesAuditorsGroup)

    permissions = PermissionsSlot(AuthActivitiesPermissions)

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    failure = Slot(BaseAuthActivityFailure)  # type: ignore[type-abstract]

    op_list = Factory(AuthListActivitiesOperation)

    cmd_list = Slot(AuthListActivitiesCommand)

    @t.final
    async def record(
        self,
        owner: Entity,
        entity_id: str,
        action: AuthActivityAction,
        metadata: OperationMetadata,
        *,
        context: AuthActivityContext | None = None,
    ) -> None:
        """
        Records a change of state of an entity of a unit, ``owner``, whose full
        name is the type of the entity, by the caller of the metadata, in its
        run, in the transaction open if one is. A failure to write it is for
        the strategy in the slot ``failure``.
        """
        caller = metadata.caller
        record = AuthActivityRecord(
            who=caller.uid,
            session_id=caller.session_id if isinstance(caller, AuthCaller) else None,
            action=action,
            entity_type=owner.full_name,
            entity_id=entity_id,
            context=_build_context(context),
            run_uid=metadata.run_uid,
            when=self._get_now(),
        )
        try:
            await self.project.auth.storage.activities.append(record)
        except Exception as error:
            self.failure.handle(error, record)

    def _get_now(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)


def _build_context(context: AuthActivityContext | None) -> dict[str, object]:
    if context is None:
        return {}
    return t.cast("dict[str, object]", _build_value(dataclasses.asdict(context)))


def _build_value(value: object) -> object:
    # the plain values a storage keeps: a tuple a list, a set a sorted one
    if isinstance(value, dict):
        return {key: _build_value(item) for key, item in value.items()}
    if isinstance(value, (frozenset, set)):
        return [_build_value(item) for item in sorted(value)]
    if isinstance(value, (list, tuple)):
        return [_build_value(item) for item in value]
    return value
