"""The command of the read of the activity log."""

__all__ = ("AuthActivitiesCommandsUnit", "AuthListActivitiesCommand")

import argparse
import datetime
import json
import typing as t

from ingots.defaults.cli import CommandsUnit
from ingots.defaults.operations import BaseOperationCommand
from ingots.puer import Slot

from ingot_auth.activities.operations import AuthListActivitiesParameters
from ingot_auth.storages import AuthActivityAction, AuthActivityRecord

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject

    from ingot_auth.activities.operations import AuthListActivitiesOperation


class AuthListActivitiesCommand(
    BaseOperationCommand[AuthListActivitiesParameters, tuple[AuthActivityRecord, ...]]
):
    """
    Prints the activities, one a line, the newest first: the time, who, its
    session or ``-``, the action, the type and the id of the entity, the run,
    then the context, ``tag_uids=[1, 3]``.
    """

    project: "AuthProject"

    cli_description = (
        "Prints the activities, the newest first, of an entity, --entity "
        "TYPE[:ID], of a caller, --who, of a session, --session, of an action, "
        "--action, since and until a time of ISO 8601 with its offset."
    )
    cli_args: AuthListActivitiesParameters

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--entity", dest="activities_entity", metavar="TYPE[:ID]")
        parser.add_argument("--who", dest="activities_who")
        parser.add_argument("--session", dest="activities_session")
        parser.add_argument(
            "--action",
            dest="activities_action",
            type=AuthActivityAction,
            choices=list(AuthActivityAction),
        )
        for name in ("since", "until"):
            parser.add_argument(
                f"--{name}", dest=f"activities_{name}", type=_parse_moment
            )
        parser.add_argument("--limit", dest="activities_limit", type=int, default=100)

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthListActivitiesParameters:
        entity_type, _, entity_uid = (namespace.activities_entity or "").partition(":")
        return AuthListActivitiesParameters(
            entity_type=entity_type or None,
            entity_uid=entity_uid or None,
            who=namespace.activities_who,
            session_uid=namespace.activities_session,
            action=namespace.activities_action,
            since=namespace.activities_since,
            until=namespace.activities_until,
            limit=namespace.activities_limit,
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListActivitiesOperation]":
        return self.project.auth.activities.op_list

    @t.override
    async def _run(self) -> None:
        for record in await self.run_operation(self.cli_args):
            context = (
                f"{key}={json.dumps(value, default=str)}"
                for key, value in sorted(record.context.items())
            )
            print(
                "\t".join(
                    (
                        record.when.isoformat(),
                        record.who,
                        record.session_uid or "-",
                        record.action,
                        record.entity_type,
                        record.entity_uid,
                        record.run_uid,
                        *context,
                    )
                )
            )


def _parse_moment(text: str) -> datetime.datetime:
    moment = datetime.datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise argparse.ArgumentTypeError(f"{text!r} has no offset")
    return moment


class AuthActivitiesCommandsUnit(CommandsUnit):
    cli_description = "The activity log: every change of state of the auth."
    list = Slot(AuthListActivitiesCommand)
