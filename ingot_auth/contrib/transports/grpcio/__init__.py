"""
The auth over gRPC, with the extra ``grpcio``, laid out by the subdomains of the
auth, ``profiles``, ``sessions``, ``access``, ``metadata`` and ``methods``: a
service per registry and per method, each in a binding of its own, so that a
server serves the ones it should; a public server the metadata and the
methods the application takes, an internal one the administration too::

    class AppGrpcServer(
        AuthGrpcMetadataBinding, AuthGrpcNicknameBinding, DefaultGrpcServer
    ):
        pass


    class AppGrpcErrors(AuthGrpcErrorsUnit):
        pass

A call bears the token of its session, ``authorization: Bearer <token>``, and
runs for its caller, with the permissions its groups grant; a call with no
token for the anonymous one, so that the administration lets in only the
users of its groups (``_get_caller()``). The metadata and the methods run for
the anonymous one, whatever the call bears.
"""

__all__ = (
    "AuthGrpcAccessBinding",
    "AuthGrpcAdminBinding",
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcErrorsUnit",
    "AuthGrpcGroupsBinding",
    "AuthGrpcGroupsServicer",
    "AuthGrpcMembersBinding",
    "AuthGrpcMembersServicer",
    "AuthGrpcMetadataBinding",
    "AuthGrpcMetadataServicer",
    "AuthGrpcNicknameBinding",
    "AuthGrpcNicknameServicer",
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

from .access import (
    AuthGrpcAccessBinding,
    AuthGrpcGroupsBinding,
    AuthGrpcGroupsServicer,
    AuthGrpcMembersBinding,
    AuthGrpcMembersServicer,
)
from .base import BaseAuthGrpcServicer
from .errors import AuthGrpcErrorsUnit
from .metadata import AuthGrpcMetadataBinding, AuthGrpcMetadataServicer
from .methods import AuthGrpcNicknameBinding, AuthGrpcNicknameServicer
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


class AuthGrpcAdminBinding(
    AuthGrpcProfilesBinding, AuthGrpcSessionsBinding, AuthGrpcAccessBinding
):
    pass
