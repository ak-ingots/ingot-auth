"""The command of the values of the attributes of the profiles."""

__all__ = ("AuthProfileAttrValuesArgs", "AuthSetProfileAttrValuesCommand")

import argparse
import datetime
import decimal
import typing as t
from dataclasses import dataclass

from ingot_auth.profiles.commands import BaseAuthProfileValuesCommand
from ingot_auth.profiles.items import AuthSetProfileAttrValuesParameters
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import AuthAttrType, AuthAttrValue

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.profiles.operations import AuthSetProfileAttrValuesOperation


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthProfileAttrValuesArgs:
    """The uid of a profile and the values as typed, by the ids of the attributes."""

    uid: str
    attr_values: tuple[tuple[int, str], ...]


class AuthSetProfileAttrValuesCommand(
    BaseAuthProfileValuesCommand[AuthSetProfileAttrValuesParameters]
):
    """
    Sets the values of the attributes of a profile, ``--value 2=2026-01-01T00:00
    +00:00``, each read by the type of its attribute, then prints its values.
    """

    cli_name = "set"
    cli_description = (
        "Sets the values of the attributes of a profile, all of them, each "
        "--value ID=VALUE: true or false, a number, a decimal, a time of ISO 8601 "
        "with its offset, a text; none takes them all off."
    )
    cli_args: AuthProfileAttrValuesArgs

    @t.override
    @classmethod
    def _cli_prepare_parser(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("profiles_uid", metavar="uid")
        parser.add_argument(
            "--value",
            dest="profiles_values",
            metavar="ID=VALUE",
            type=_parse_assignment,
            action="append",
            default=[],
        )

    @t.override
    @classmethod
    def _cli_build_args(
        cls, namespace: argparse.Namespace
    ) -> AuthProfileAttrValuesArgs:
        return AuthProfileAttrValuesArgs(
            uid=namespace.profiles_uid, attr_values=tuple(namespace.profiles_values)
        )

    @t.override
    def _get_operation(self) -> "BoundFactory[AuthSetProfileAttrValuesOperation]":
        return self.project.auth.profiles.op_set_attr_values

    @t.override
    async def _run(self) -> None:
        attrs = self.project.auth.storage.profiles.attrs
        types = {attr.id: attr.type for attr in await attrs.get_all()}
        attr_values = {
            # one of no attribute is left as typed: the operation refuses it
            attr_id: (
                parse_attr_value(attrs.REGISTRY, attr_id, types[attr_id], text)
                if attr_id in types
                else text
            )
            for attr_id, text in self.cli_args.attr_values
        }
        parameters = AuthSetProfileAttrValuesParameters(
            uid=self.cli_args.uid, attr_values=attr_values
        )
        self.print_values(await self.run_operation(parameters))


def parse_attr_value(
    registry: str, attr_id: int, attr_type: AuthAttrType, text: str
) -> AuthAttrValue:
    """
    Internal: a value as typed, by the type of its attribute.

    :raises AuthItemInvalidError: it is not one of the type.
    """
    try:
        match attr_type:
            case AuthAttrType.BOOL:
                return {"true": True, "false": False}[text]
            case AuthAttrType.INT:
                return int(text)
            case AuthAttrType.DECIMAL:
                number = decimal.Decimal(text)
                if not number.is_finite():
                    raise ValueError(text)
                return number
            case AuthAttrType.DATETIME:
                moment = datetime.datetime.fromisoformat(text)
                if moment.tzinfo is None:
                    raise ValueError(text)
                return moment
            case _:  # a text
                return text
    except KeyError, ValueError, decimal.InvalidOperation:
        raise AuthItemInvalidError.for_value(registry, attr_id) from None


def _parse_assignment(text: str) -> tuple[int, str]:
    attr_id, separator, value = text.partition("=")
    if not separator:
        raise argparse.ArgumentTypeError(f"{text!r} is not ID=VALUE")
    try:
        return int(attr_id), value
    except ValueError:
        raise argparse.ArgumentTypeError(f"{attr_id!r} is not an id") from None
