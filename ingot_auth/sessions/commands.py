"""The commands of the sessions."""

__all__ = (
    "AuthListSessionsCommand",
    "AuthRevokeAllSessionsCommand",
    "AuthSessionsCommandsUnit",
    "AuthSweepSessionsCommand",
)

import argparse
import typing as t

from ingots.defaults.cli import CommandsUnit
from ingots.defaults.operations import BaseOperationCommand
from ingots.puer import Slot

from .attrs.commands import AuthSessionAttrsCommandsUnit
from .data import AuthSessionInfo
from .operations import (
    AuthListSessionsOperation,
    AuthListSessionsParameters,
    AuthRevokeAllSessionsOperation,
    AuthRevokeAllSessionsParameters,
    AuthSweepSessionsOperation,
    AuthSweepSessionsParameters,
)
from .presets.commands import AuthSessionPresetsCommandsUnit

if t.TYPE_CHECKING:
    from ingots.defaults.operations import Caller
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class AuthListSessionsCommand(
    BaseOperationCommand[AuthListSessionsParameters, tuple[AuthSessionInfo, ...]]
):
    """
    Prints the sessions of a profile, one a line, by the time they opened: the
    uid, the method, the times it opened and was seen at, then, closed, the
    time and the reason, and the values of its attributes, ``1=iPhone``.
    """

    project: "AuthProject"

    cli_description = (
        "Prints the open sessions of a profile, the closed ones too if told "
        "--closed: the record of its sign-ins."
    )
    cli_args: AuthListSessionsParameters

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("sessions_uid", metavar="uid")
        parser.add_argument("--closed", dest="sessions_closed", action="store_true")

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthListSessionsParameters:
        return AuthListSessionsParameters(
            profile_uid=namespace.sessions_uid, closed=namespace.sessions_closed
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthListSessionsOperation]":
        return self.project.auth.sessions.op_list

    @t.override
    async def _run(self) -> None:
        for session in await self.run_operation(self.cli_args):
            closed = (
                (
                    session.closed_at.isoformat(),
                    str(session.close_reason),
                )
                if session.closed_at
                else ()
            )
            values = (
                f"{key}={value}" for key, value in sorted(session.attr_values.items())
            )
            print(
                "\t".join(
                    (
                        session.uid,
                        session.method,
                        session.opened_at.isoformat(),
                        session.seen_at.isoformat(),
                        *closed,
                        *values,
                    )
                )
            )


class AuthRevokeAllSessionsCommand(
    BaseOperationCommand[AuthRevokeAllSessionsParameters, int]
):
    """Revokes every open session of a profile and prints how many."""

    project: "AuthProject"

    cli_description = "Revokes every open session of a profile: a stolen account."
    cli_args: AuthRevokeAllSessionsParameters

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("sessions_profile_uid", metavar="profile_uid")

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthRevokeAllSessionsParameters:
        return AuthRevokeAllSessionsParameters(
            profile_uid=namespace.sessions_profile_uid
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthRevokeAllSessionsOperation]":
        return self.project.auth.sessions.op_revoke_all

    @t.override
    async def _run(self) -> None:
        print(await self.run_operation(self.cli_args))


class AuthSweepSessionsCommand(BaseOperationCommand[AuthSweepSessionsParameters, int]):
    """
    Sweeps the expired sessions and prints how many: a job of a schedule of
    the application, cron or another, run as ``auth.system``.
    """

    project: "AuthProject"

    cli_description = "Closes the expired sessions: a job of a schedule."
    cli_args: AuthSweepSessionsParameters

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthSweepSessionsParameters:
        return AuthSweepSessionsParameters()

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthSweepSessionsOperation]":
        return self.project.auth.sessions.op_sweep

    @t.override
    def _get_caller(self) -> "Caller":
        return self.project.operations.callers.get_auth_system()

    @t.override
    async def _run(self) -> None:
        print(await self.run_operation(self.cli_args))


class AuthSessionsCommandsUnit(CommandsUnit):
    cli_description = "The sessions of the users."
    list = Slot(AuthListSessionsCommand)
    revoke_all = Slot(AuthRevokeAllSessionsCommand)
    sweep = Slot(AuthSweepSessionsCommand)
    attrs = Slot(AuthSessionAttrsCommandsUnit)
    presets = Slot(AuthSessionPresetsCommandsUnit)
