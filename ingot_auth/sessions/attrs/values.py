"""
The values of the attributes of a session: of a client, a transport, and
derived from them.
"""

__all__ = ("build_attr_values", "check_client_attr_values")

import logging
import typing as t

from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.storages import (
    ATTR_VALUE_TYPES,
    AuthAttrValue,
    AuthItemNotFoundError,
    AuthSessionAttr,
    AuthSessionAttrSource,
)

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

REGISTRY: t.Final = "sessions.attrs"

logger = logging.getLogger(__name__)


def check_client_attr_values(
    attrs: "Iterable[AuthSessionAttr]", attr_values: "Mapping[int, AuthAttrValue]"
) -> None:
    """
    Checks the values a client gives, by the id of their attributes: each of
    an attribute there is, of its type, and of the client. A client never
    gives what the transport, the provider or the server do.

    :raises AuthItemNotFoundError: no attribute has the id.
    :raises AuthItemInvalidError: the value is not of the type of its
        attribute, or the client is not its source.
    """
    by_id = {attr.uid: attr for attr in attrs}
    for attr_uid, value in attr_values.items():
        try:
            attr = by_id[attr_uid]
        except KeyError:
            raise AuthItemNotFoundError.for_uid(REGISTRY, attr_uid) from None
        if attr.source is not AuthSessionAttrSource.CLIENT:
            raise AuthItemInvalidError.for_value(REGISTRY, attr_uid)
        if type(value) is not ATTR_VALUE_TYPES[attr.type]:
            raise AuthItemInvalidError.for_value(REGISTRY, attr_uid)


def build_attr_values(
    attrs: "Iterable[AuthSessionAttr]",
    attr_values: "Mapping[str, AuthAttrValue]",
    source: AuthSessionAttrSource,
) -> dict[int, AuthAttrValue]:
    """
    The values a transport gives, or the server derives, by the names of their
    attributes, kept by the ids of the attributes of the registry of their
    source: the source gives what it has, the registry tells what is kept. A
    value of no attribute is dropped, the application keeping none of it;
    one of an attribute of another source or of another type is dropped too,
    with a warning, as the registry is wrong then, not the call.
    """
    by_name = {attr.name: attr for attr in attrs}
    kept: dict[int, AuthAttrValue] = {}
    for name, value in attr_values.items():
        try:
            attr = by_name[name]
        except KeyError:
            continue
        if attr.source is not source:
            logger.warning(
                "the attribute %r of the sessions is of the source %s: "
                "the value of the %s is dropped",
                name,
                attr.source,
                source,
            )
        elif type(value) is not ATTR_VALUE_TYPES[attr.type]:
            logger.warning(
                "the attribute %r of the sessions is of the type %s, the value "
                "of the %s a %s: it is dropped",
                name,
                attr.type,
                source,
                type(value).__name__,
            )
        else:
            kept[attr.uid] = value
    return kept
