"""The values the parts of the cache in Redis keep, as those of JSON."""

__all__ = (
    "build_attr_values",
    "build_json_attr_values",
    "build_json_time",
    "build_time",
)

import datetime
import decimal
import typing as t

from ingot_auth.storages import ATTR_VALUE_TYPES, AuthAttrType

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


def build_json_attr_values(
    attr_values: "Mapping[int, AuthAttrValue]",
) -> list[list[object]]:
    """
    The values of the attributes for JSON: the id of the attribute, the type
    of the value and the value, a decimal and a time as strings.
    """
    return [
        [attr_uid, *_build_json_value(value)] for attr_uid, value in attr_values.items()
    ]


def build_attr_values(data: list[list[t.Any]]) -> "dict[int, AuthAttrValue]":
    """The values of the attributes from JSON, as given to it."""
    return {
        attr_uid: _build_value(AuthAttrType(kind), value)
        for attr_uid, kind, value in data
    }


def build_json_time(time: datetime.datetime) -> str:
    return time.isoformat()


def build_time(data: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(data)


def _build_json_value(value: "AuthAttrValue") -> tuple[str, object]:
    # exactly, a bool is not an int here
    kind = next(k for k, cls in ATTR_VALUE_TYPES.items() if type(value) is cls)
    match value:
        case decimal.Decimal():
            return kind, str(value)
        case datetime.datetime():
            return kind, build_json_time(value)
    return kind, value


def _build_value(kind: AuthAttrType, value: t.Any) -> "AuthAttrValue":
    match kind:
        case AuthAttrType.DECIMAL:
            return decimal.Decimal(value)
        case AuthAttrType.DATETIME:
            return build_time(value)
    return t.cast("AuthAttrValue", value)
