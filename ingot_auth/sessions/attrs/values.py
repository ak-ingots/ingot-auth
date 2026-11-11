"""The values of the attributes of a session, as a client gives them."""

__all__ = ("check_client_values",)

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


def check_client_values(
    attrs: "Iterable[AuthSessionAttr]", values: "Mapping[int, AuthAttrValue]"
) -> None:
    """
    Checks the values a client gives, by the id of their attributes: each of
    an attribute there is, of its type, and of the client. A client never
    gives what the transport, the provider or the server do.

    :raises AuthItemNotFoundError: no attribute has the id.
    :raises AuthItemInvalidError: the value is not of the type of its
        attribute, or the client is not its source.
    """
    by_id = {attr.id: attr for attr in attrs}
    for attr_id, value in values.items():
        try:
            attr = by_id[attr_id]
        except KeyError:
            raise AuthItemNotFoundError.for_id(REGISTRY, attr_id) from None
        if attr.source is not AuthSessionAttrSource.CLIENT:
            raise AuthItemInvalidError.for_value(REGISTRY, attr_id)
        if type(value) is not ATTR_VALUE_TYPES[attr.type]:
            raise AuthItemInvalidError.for_value(REGISTRY, attr_id)
