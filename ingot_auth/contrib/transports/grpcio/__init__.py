"""
The auth over gRPC, with the extra ``grpcio``, laid out by the subdomains of the
auth, ``profiles``, ``sessions``, ``access``, ``metadata`` and ``methods``: a
service per registry and per method, each in a binding of its own, so that a
server serves the ones it should; a public server the metadata and the
methods the application takes, with the answers of the flows for a method
of more steps and the sign-out, an internal one the administration too::

    class AppGrpcServer(
        AuthGrpcMetadataBinding,
        AuthGrpcNicknameBinding,
        AuthGrpcEmailCodeBinding,
        AuthGrpcFlowsBinding,
        DefaultGrpcServer,
    ):
        pass


    class AppGrpcErrors(AuthGrpcErrorsUnit):
        pass

A call bears the token of its session, ``authorization: Bearer <token>``, and
runs for its caller, with the permissions its groups grant; a call with no
token for the anonymous one, so that the administration lets in only the
users of its groups (``_get_caller()``). The metadata, the methods and the
answers of the flows run for the anonymous one, whatever the call bears; the
sign-out for the caller of the token, the anonymous one of a token closed,
expired or unknown, which signs out of nothing.
"""

__all__ = (
    "AuthGrpcAccessBinding",
    "AuthGrpcAdminBinding",
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcEmailCodeBinding",
    "AuthGrpcEmailCodeServicer",
    "AuthGrpcErrorsUnit",
    "AuthGrpcFlowsBinding",
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
    "AuthGrpcSessionRegistriesBinding",
    "AuthGrpcSessionsBinding",
    "AuthGrpcSessionsServicer",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
    "AuthGrpcSignInBinding",
    "AuthGrpcSignInServicer",
    "AuthGrpcSignOutBinding",
    "AuthGrpcSignOutServicer",
    "AuthGrpcSignUpBinding",
    "AuthGrpcSignUpServicer",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
    "BaseAuthGrpcMethodServicer",
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
from .methods import (
    AuthGrpcEmailCodeBinding,
    AuthGrpcEmailCodeServicer,
    AuthGrpcNicknameBinding,
    AuthGrpcNicknameServicer,
    BaseAuthGrpcMethodServicer,
)
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
    AuthGrpcSessionRegistriesBinding,
    AuthGrpcSessionsBinding,
    AuthGrpcSessionsServicer,
    AuthGrpcSessionPresetsBinding,
    AuthGrpcSessionPresetsServicer,
)
from .sign_in import AuthGrpcSignInBinding, AuthGrpcSignInServicer
from .sign_out import AuthGrpcSignOutBinding, AuthGrpcSignOutServicer
from .sign_up import AuthGrpcSignUpBinding, AuthGrpcSignUpServicer


class AuthGrpcFlowsBinding(
    AuthGrpcSignUpBinding, AuthGrpcSignInBinding, AuthGrpcSignOutBinding
):
    """The answers of the flows, for the methods of more steps, and the sign-out."""


class AuthGrpcAdminBinding(
    AuthGrpcProfilesBinding, AuthGrpcSessionRegistriesBinding, AuthGrpcAccessBinding
):
    pass
