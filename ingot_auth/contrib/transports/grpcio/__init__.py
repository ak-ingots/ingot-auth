"""
The auth over gRPC, with the extra ``grpcio``, laid out by the subdomains of the
auth, ``profiles``, ``sessions`` and ``metadata``: a service per registry, each
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
    "AuthGrpcProfilesBinding",
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionsBinding",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
    "BaseAuthGrpcServicer",
)

from .base import BaseAuthGrpcServicer
from .errors import AuthGrpcErrors
from .metadata import AuthGrpcMetadataBinding, AuthGrpcMetadataServicer
from .profiles import (
    AuthGrpcAttrsBinding,
    AuthGrpcAttrsServicer,
    AuthGrpcProfilesBinding,
    AuthGrpcTagsBinding,
    AuthGrpcTagsServicer,
)
from .sessions import (
    AuthGrpcSessionAttrsBinding,
    AuthGrpcSessionAttrsServicer,
    AuthGrpcSessionsBinding,
    AuthGrpcSessionPresetsBinding,
    AuthGrpcSessionPresetsServicer,
)


class AuthGrpcAdminBinding(AuthGrpcProfilesBinding, AuthGrpcSessionsBinding):
    pass
