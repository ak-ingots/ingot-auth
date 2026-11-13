"""The base of the servicers of the methods."""

__all__ = ("BaseAuthGrpcMethodServicer",)

import typing as t

from ingot_grpcio.grpc.services import GrpcServicer

from ..base import Context, get_peer_ip

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject
    from ingot_auth.storages import AuthAttrValue


class BaseAuthGrpcMethodServicer(GrpcServicer):
    """
    A servicer of a method, its starts open to anyone, as every flow is: they
    run for the anonymous caller of the project, whatever a call bears,
    given the flags of the flows by the group ``grp_anonymous``.
    :attr:`METHOD` is the name of the slot of the method it serves: an
    application binding the method under another name subclasses it. A start
    gives the values of the attributes of the transport,
    :meth:`get_transport_attr_values`, kept as the registry of the
    attributes of the sessions has them, of the source ``transport``.
    """

    # the name of the method served: the path of its slot in the methods
    METHOD: t.ClassVar[str]

    project: "AuthProject"

    @t.final
    def get_transport_attr_values(self, context: Context) -> "dict[str, AuthAttrValue]":
        """The values of the attributes of the transport of a call, by name."""
        return {
            name: value
            for name, value in self._get_transport_attr_values(context).items()
            if value is not None
        }

    def _get_transport_attr_values(
        self, context: Context
    ) -> "dict[str, AuthAttrValue | None]":
        """
        The attributes of the transport by their names, each bound to the
        function reading its value from the call, ``None`` for a call without
        one: ``ip``, the IP of the peer, here. Each class adds its own to
        ``super()``, or binds a name to another function: behind a proxy,
        ``ip`` to a reader of the header the proxy sets, trusted from the
        proxy alone, in a mixin of the application extending this class,
        mixed into each servicer of a method::

            @t.override
            def _get_transport_attr_values(self, context):
                return super()._get_transport_attr_values(context) | {
                    "ip": get_forwarded_ip(context),
                }
        """
        # the one way of binding them for now; a strategy in a slot later, as
        # for the token of a call
        return {"ip": get_peer_ip(context)}
