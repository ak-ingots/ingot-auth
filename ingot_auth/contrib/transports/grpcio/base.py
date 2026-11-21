"""The base of the servicers."""

__all__ = (
    "PROFILE_HASH_KEY",
    "BaseAuthGrpcServicer",
    "Context",
    "GrpcAuthRpcContext",
    "get_bearer_token",
    "get_peer_ip",
)

import ipaddress
import typing as t
import urllib.parse

from grpc import aio
from ingot_grpcio.grpc.services import GrpcServicer
from ingots.defaults.operations import Caller

from ..contract import (
    PROFILE_HASH_KEY,
    AuthSessionRpcMixin,
    BaseAuthRpcContext,
    parse_bearer_token,
)

if t.TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue

Context: t.TypeAlias = aio.ServicerContext[t.Any, t.Any]


class GrpcAuthRpcContext(BaseAuthRpcContext):
    """
    The context of a call of gRPC as the RPCs of the auth see it: its
    invocation metadata, the values of the attributes of its transport its
    servicer reads, the hash of the profile in its trailing metadata.
    """

    def __init__(
        self,
        context: Context,
        transport_attr_values: "Callable[[], dict[str, AuthAttrValue]]" = dict,
    ) -> None:
        self._context = context
        self._transport_attr_values = transport_attr_values

    @t.override
    def get_metadata(self, key: str) -> str | None:
        for name, value in self._context.invocation_metadata() or ():
            if name == key and isinstance(value, str):
                return value
        return None

    @t.override
    def get_transport_attr_values(self) -> "dict[str, AuthAttrValue]":
        return self._transport_attr_values()

    @t.override
    def set_profile_hash(self, profile_hash: str) -> None:
        self._context.set_trailing_metadata(((PROFILE_HASH_KEY, profile_hash),))


class BaseAuthGrpcServicer(AuthSessionRpcMixin, GrpcServicer):
    """
    A servicer of the auth: an RPC turns its request into the parameters of an
    operation and the result into its reply, nothing else, the RPCs of
    :mod:`~ingot_auth.contrib.transports.contract` mixed in where they are
    shared with HTTP. The operation runs for the caller of the session of the
    token of a call, ``Bearer <token>`` in the header ``authorization``, or with
    no token the anonymous one of the project,
    ``operations.callers.get_anonymous()``; its exceptions reach the policies of
    :class:`~..errors.AuthGrpcErrorsUnit`. A servicer of an application serving
    signed-in callers extends it too: every reply to one tells the hash of its
    profile in its trailing metadata, ``PROFILE_HASH_KEY``, no interceptor,
    which would see no caller; a reply refused tells it not, the refusal itself
    telling the client to ask again. A servicer open to anyone extends
    ``GrpcServicer`` alone, so that it runs for the anonymous one, whatever the
    call bears.
    """

    project: "AuthProject"

    @t.override
    async def _get_caller(self, context: Context) -> Caller:
        """
        :raises AuthSessionNotFoundError: no open session has the token.
        :raises AuthSessionExpiredError: its session expired, closed now.
        """
        return await self._rpc_get_caller(GrpcAuthRpcContext(context))


def get_bearer_token(
    metadata: "Iterable[tuple[str, str | bytes]] | None",
) -> str | None:
    """
    The token of the header ``authorization`` of a call, of the scheme
    ``Bearer`` in any case (RFC 6750), ``None`` without one: a header of
    another scheme tells no token either.
    """
    for key, value in metadata or ():
        if key == "authorization" and isinstance(value, str):
            return parse_bearer_token(value)
    return None


def get_peer_ip(context: Context) -> str | None:
    """
    The IP of the peer of a call, as grpcio tells it,
    ``ipv4:10.0.0.1:5000``, ``ipv6:[::1]:5000``, escaped by some versions,
    ``ipv6:%5B::1%5D:5000``; an IPv4 mapped to IPv6 as the IPv4; ``None``
    for a peer of no IP, a Unix socket. Behind a proxy it is the proxy.
    """
    scheme, _, address = urllib.parse.unquote(context.peer()).partition(":")
    if scheme not in ("ipv4", "ipv6"):
        return None
    host = address.rpartition(":")[0].removeprefix("[").removesuffix("]")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return None
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return str(ip.ipv4_mapped)
    return str(ip)
