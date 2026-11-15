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
        tag_ids = (str(tag_id) for tag_id in sorted(values.tag_ids))
        print("\t".join(("tags", *tag_ids)))
        attr_values = (
            f"{attr_id}={_format_attr_value(value)}"
            for attr_id, value in sorted(values.attr_values.items())
        )
        print("\t".join(("attrs", *attr_values)))


def _format_attr_value(value: AuthAttrValue) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return str(value)
