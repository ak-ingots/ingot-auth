"""The base of the endpoints of the auth over HTTP."""

__all__ = (
    "PROFILE_HASH_STATE",
    "BaseAuthStarletteEndpoint",
    "StarletteAuthRpcContext",
)

import typing as t

from ingot_starlette.contrib.protobuf import BaseStarletteProtobufEndpoint

from ingot_auth.api import BaseAuthRpcContext

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.requests import Request

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue

# the key of the state of a request telling the hash of the profile of its
# caller, which AuthStarletteProfileHashMiddleware tells in the response
PROFILE_HASH_STATE: t.Final = "ingot_auth_profile_hash"


class StarletteAuthRpcContext(BaseAuthRpcContext):
    """
    A request of HTTP as the RPCs of the auth see it: its headers, the
    values of the attributes of its transport its endpoint reads, the hash
    of the profile in its state, for the middleware to tell it.
    """

    def __init__(
        self,
        request: "Request",
        transport_attr_values: "Callable[[], dict[str, AuthAttrValue]]" = dict,
    ) -> None:
        self._request = request
        self._transport_attr_values = transport_attr_values

    @t.override
    def get_metadata(self, key: str) -> str | None:
        return self._request.headers.get(key)

    @t.override
    def get_transport_attr_values(self) -> "dict[str, AuthAttrValue]":
        return self._transport_attr_values()

    @t.override
    def set_profile_hash(self, profile_hash: str) -> None:
        self._request.scope.setdefault("state", {})[PROFILE_HASH_STATE] = profile_hash


class BaseAuthStarletteEndpoint(BaseStarletteProtobufEndpoint):
    """
    An endpoint of the auth over HTTP: the RPCs of a mixin of the contract,
    transcoded by the annotations ``google.api.http`` of their methods, each
    handler adapting its request to the context of the RPC by
    :meth:`get_rpc_context`. A start of a method gives the values of the
    attributes of the transport, :meth:`_get_transport_attr_values`.
    """

    project: "AuthProject"

    @t.final
    def get_rpc_context(self, request: "Request") -> StarletteAuthRpcContext:
        """The context of a request, as the RPCs of the auth see it."""
        return StarletteAuthRpcContext(
            request, lambda: self.get_transport_attr_values(request)
        )

    @t.final
    def get_transport_attr_values(
        self, request: "Request"
    ) -> "dict[str, AuthAttrValue]":
        """The values of the attributes of the transport of a request, by name."""
        return {
            name: value
            for name, value in self._get_transport_attr_values(request).items()
            if value is not None
        }

    def _get_transport_attr_values(
        self, request: "Request"
    ) -> "dict[str, AuthAttrValue | None]":
        """
        The attributes of the transport by their names, each read from the
        request, ``None`` of one without it: ``ip``, the client of the
        connection, here. Behind a proxy the server tells the forwarded one,
        ``uvicorn --proxy-headers``, or a subclass reads the header of the
        proxy, trusted from the proxy alone.
        """
        return {"ip": request.client.host if request.client else None}
