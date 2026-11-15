"""The commands of the sessions."""

__all__ = ("AuthListSessionsCommand",)

import argparse
import typing as t

from ingots.defaults.operations import BaseOperationCommand

from .items import AuthListSessionsParameters, AuthSessionInfo
from .operations import AuthListSessionsOperation

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class AuthListSessionsCommand(
    BaseOperationCommand[AuthListSessionsParameters, tuple[AuthSessionInfo, ...]]
):
    """
    Prints the sessions of a profile, one a line, by the time they opened: the
    id, the method, the times it opened and was seen at, then, closed, the time,
    the reason and by whom, ``-`` when it expired, and the values of its
    attributes, ``1=iPhone``.
    """

    project: "AuthProject"

    cli_name = "list"
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
            uid=namespace.sessions_uid, closed=namespace.sessions_closed
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
                    session.closed_by or "-",
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
                        session.id,
                        session.method,
                        session.opened_at.isoformat(),
                        session.seen_at.isoformat(),
                        *closed,
                        *values,
                    )
                )
            )
