"""The activity log over gRPC."""

__all__ = ("ACTIONS", "AuthGrpcActivitiesBinding", "AuthGrpcActivitiesServicer")

import datetime
import decimal
import typing as t
from datetime import UTC

from ingot_grpcio.grpc.services import GrpcService

from ingot_auth.activities import AuthListActivitiesParameters
from ingot_auth.storages import AuthActivityAction, AuthActivityRecord

from .base import BaseAuthGrpcServicer, Context
from ingot_auth.api.activities.v1 import activities_pb2, activities_pb2_grpc

#: The action of an activity as the contract names it, each of the domain.
ACTIONS: t.Final[dict[AuthActivityAction, activities_pb2.Action.ValueType]] = {
    AuthActivityAction.CREATE: activities_pb2.ACTION_CREATE,
    AuthActivityAction.UPDATE: activities_pb2.ACTION_UPDATE,
    AuthActivityAction.DELETE: activities_pb2.ACTION_DELETE,
    AuthActivityAction.BIND: activities_pb2.ACTION_BIND,
    AuthActivityAction.UNBIND: activities_pb2.ACTION_UNBIND,
    AuthActivityAction.SIGN_IN: activities_pb2.ACTION_SIGN_IN,
    AuthActivityAction.SIGN_OUT: activities_pb2.ACTION_SIGN_OUT,
    AuthActivityAction.REVOKE: activities_pb2.ACTION_REVOKE,
    AuthActivityAction.EXPIRE: activities_pb2.ACTION_EXPIRE,
    AuthActivityAction.EVICT: activities_pb2.ACTION_EVICT,
}
ACTIONS_BY_MESSAGE: t.Final = {message: action for action, message in ACTIONS.items()}


class AuthGrpcActivitiesServicer(
    BaseAuthGrpcServicer, activities_pb2_grpc.ActivitiesServicer
):
    """The activity log, read by the auditors."""

    @t.override
    async def ListActivities(
        self, request: activities_pb2.ListActivitiesRequest, context: Context
    ) -> activities_pb2.ListActivitiesResponse:
        has = request.HasField
        parameters = AuthListActivitiesParameters(
            entity_type=request.entity_type if has("entity_type") else None,
            entity_uid=request.entity_uid if has("entity_uid") else None,
            who=request.who if has("who") else None,
            session_uid=request.session_uid if has("session_uid") else None,
            action=ACTIONS_BY_MESSAGE.get(request.action),
            since=request.since.ToDatetime(tzinfo=UTC) if has("since") else None,
            until=request.until.ToDatetime(tzinfo=UTC) if has("until") else None,
            limit=request.limit or 100,
        )
        factory = self.project.auth.activities.op_list
        records = await self.run_operation(factory, parameters, context)
        return activities_pb2.ListActivitiesResponse(
            activities=[build_activity_message(record) for record in records]
        )


class AuthGrpcActivitiesBinding:
    auth_activities = GrpcService(
        activities_pb2_grpc.ActivitiesStub, AuthGrpcActivitiesServicer
    )


def build_activity_message(record: AuthActivityRecord) -> activities_pb2.Activity:
    """Internal: the message of a record of the log, its context a struct."""
    message = activities_pb2.Activity(
        who=record.who,
        session_uid=record.session_uid or "",
        action=ACTIONS[record.action],
        entity_type=record.entity_type,
        entity_uid=record.entity_uid,
        run_uid=record.run_uid,
    )
    message.context.update(t.cast("dict[str, t.Any]", _build_json(record.context)))
    message.when.FromDatetime(record.when)
    return message


def _build_json(value: object) -> object:
    # what a struct of protobuf takes: a decimal and a time as texts
    if isinstance(value, (decimal.Decimal, datetime.datetime)):
        return str(value) if isinstance(value, decimal.Decimal) else value.isoformat()
    if isinstance(value, dict):
        return {key: _build_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_build_json(item) for item in value]
    return value
