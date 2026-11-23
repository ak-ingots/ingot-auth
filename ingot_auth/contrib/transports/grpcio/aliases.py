"""
Temporary: the attribute of a binding giving what another one gives, the
same servicer on a server, the same stub on a client, its service bound
once; the old names of the bindings alias those of the API, ``*_temp``,
till ``*_temp`` goes.
"""

__all__ = ("AuthGrpcServiceAlias",)

import typing as t

from ingot_grpcio.grpc.services import GrpcService, GrpcServicer

if t.TYPE_CHECKING:
    from ingot_grpcio.grpc.clients import BaseGrpcClient
    from ingot_grpcio.grpc.servers import BaseGrpcServer
    from ingot_grpcio.grpc.services import GrpcServicesOwner


class AuthGrpcServiceAlias[Stub, Servicer: GrpcServicer]:
    """The attribute of a binding giving what ``service`` gives."""

    def __init__(self, service: GrpcService[Stub, Servicer]) -> None:
        self._service = service

    @t.overload
    def __get__(self, obj: None, owner: type) -> GrpcService[Stub, Servicer]: ...

    @t.overload
    def __get__(self, obj: "BaseGrpcServer", owner: type) -> Servicer: ...

    @t.overload
    def __get__(self, obj: "BaseGrpcClient", owner: type) -> Stub: ...

    def __get__(self, obj: "GrpcServicesOwner | None", owner: type) -> object:
        if obj is None:
            return self._service
        return obj._grpc_services_get(self._service)
