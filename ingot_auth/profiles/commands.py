"""The base of the commands of the values of the profiles."""

__all__ = ("BaseAuthProfileValuesCommand",)

import datetime
import typing as t

from ingots.defaults.operations import BaseOperationCommand

from ingot_auth.storages import AuthAttrValue, AuthProfileValues

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class BaseAuthProfileValuesCommand[ParametersType](
    BaseOperationCommand[ParametersType, AuthProfileValues]
):
    """
    A command setting values of a profile, which prints them after: the tags
    in a line, ``tags\t1\t3``, the values of the attributes in another,
    ``attrs\t1=Ann\t2=true``.
    """

    project: "AuthProject"

    @t.final
    def print_values(self, values: AuthProfileValues) -> None:
        tag_uids = (str(tag_uid) for tag_uid in sorted(values.tag_uids))
        print("\t".join(("tags", *tag_uids)))
        attr_values = (
            f"{attr_uid}={_format_attr_value(value)}"
            for attr_uid, value in sorted(values.attr_values.items())
        )
        print("\t".join(("attrs", *attr_values)))


def _format_attr_value(value: AuthAttrValue) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return str(value)
