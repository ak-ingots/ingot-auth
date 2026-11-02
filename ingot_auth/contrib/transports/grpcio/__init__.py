"""
The auth over gRPC, with the extra ``grpcio``, laid out by the subdomains of the
auth, ``profile``, ``session`` and ``metadata``: a service per registry, each
in a binding of its own, so that a server serves the ones it should; a public
server the metadata, an internal one the administration too::

    class AppGrpcServer(AuthGrpcMetadataBinding, DefaultGrpcServer):
        pass


    class AppGrpcErrors(AuthGrpcErrors):
        pass

The administration lets nobody in until a subclass of its servicers tells who
is calling (``_get_caller()``).
"""

__all__ = (
    "AuthGrpcAdminBinding",
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcErrors",
    "AuthGrpcMetadataBinding",
    "AuthGrpcMetadataServicer",
    "AuthGrpcProfileBinding",
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionBinding",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
    "BaseAuthGrpcServicer",
)

from .base import BaseAuthGrpcServicer
from .errors import AuthGrpcErrors
from .metadata import AuthGrpcMetadataBinding, AuthGrpcMetadataServicer
from .profile import (
    AuthGrpcAttrsBinding,
    AuthGrpcAttrsServicer,
    AuthGrpcProfileBinding,
    AuthGrpcTagsBinding,
    AuthGrpcTagsServicer,
)
from .session import (
    AuthGrpcSessionAttrsBinding,
    AuthGrpcSessionAttrsServicer,
    AuthGrpcSessionBinding,
    AuthGrpcSessionPresetsBinding,
    AuthGrpcSessionPresetsServicer,
)


class AuthGrpcAdminBinding(AuthGrpcProfileBinding, AuthGrpcSessionBinding):
    pass
