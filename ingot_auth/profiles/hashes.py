"""The hash of what a client sees of a profile."""

__all__ = ("build_profile_hash",)

import datetime
import hashlib
import json
import typing as t

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue, AuthProfileValues


def build_profile_hash(
    values: "AuthProfileValues", permissions: "Mapping[str, int]"
) -> str:
    """
    The hash of what a client sees of a profile, its tags, the values of its
    attributes and its permissions: it changes with any of them, so that a
    client comparing it with its own knows to ask for the profile again.
    """
    content = [
        sorted(values.tag_uids),
        sorted(
            (attr_uid, type(value).__name__, _format(value))
            for attr_uid, value in values.attr_values.items()
        ),
        sorted(permissions.items()),
    ]
    text = json.dumps(content, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def _format(value: "AuthAttrValue") -> str:
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return str(value)
