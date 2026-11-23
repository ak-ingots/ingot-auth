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
    "AuthGrpcActivitiesBinding",
    "AuthGrpcActivitiesServicer",
    "AuthGrpcActivitiesServicerTemp",
    "AuthGrpcAdminBinding",
    "AuthGrpcAttrsBinding",
    "AuthGrpcAttrsServicer",
    "AuthGrpcAttrsServicerTemp",
    "AuthGrpcEmailCodeBinding",
    "AuthGrpcEmailCodeServicer",
    "AuthGrpcEmailCodeServicerTemp",
    "AuthGrpcErrorsUnit",
    "AuthGrpcFlowsBinding",
    "AuthGrpcGroupsBinding",
    "AuthGrpcGroupsServicer",
    "AuthGrpcGroupsServicerTemp",
    "AuthGrpcMembersBinding",
    "AuthGrpcMembersServicer",
    "AuthGrpcMembersServicerTemp",
    "AuthGrpcMetadataBinding",
    "AuthGrpcMetadataServicer",
    "AuthGrpcMetadataServicerTemp",
    "AuthGrpcNicknameBinding",
    "AuthGrpcNicknameServicer",
    "AuthGrpcNicknameServicerTemp",
    "AuthGrpcProfileRegistriesBinding",
    "AuthGrpcProfilesBinding",
    "AuthGrpcProfilesServicer",
    "AuthGrpcProfilesServicerTemp",
    "AuthGrpcSessionAttrsBinding",
    "AuthGrpcSessionAttrsServicer",
    "AuthGrpcSessionAttrsServicerTemp",
    "AuthGrpcSessionPresetsBinding",
    "AuthGrpcSessionPresetsServicer",
    "AuthGrpcSessionPresetsServicerTemp",
    "AuthGrpcSessionRegistriesBinding",
    "AuthGrpcSessionsBinding",
    "AuthGrpcSessionsServicer",
    "AuthGrpcSessionsServicerTemp",
    "AuthGrpcSignInBinding",
    "AuthGrpcSignInServicer",
    "AuthGrpcSignInServicerTemp",
    "AuthGrpcSignOutBinding",
    "AuthGrpcSignOutServicer",
    "AuthGrpcSignOutServicerTemp",
    "AuthGrpcSignUpBinding",
    "AuthGrpcSignUpServicer",
    "AuthGrpcSignUpServicerTemp",
    "AuthGrpcTagsBinding",
    "AuthGrpcTagsServicer",
    "AuthGrpcTagsServicerTemp",
    "BaseAuthGrpcMethodServicer",
    "BaseAuthGrpcServicer",
)

from .activities import AuthGrpcActivitiesBinding, AuthGrpcActivitiesServicer
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
    AuthGrpcProfileRegistriesBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcProfilesServicer,
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
from .access.groups_temp import AuthGrpcGroupsServicerTemp
from .access.members_temp import AuthGrpcMembersServicerTemp
from .activities_temp import AuthGrpcActivitiesServicerTemp
from .metadata_temp import AuthGrpcMetadataServicerTemp
from .methods.email_code_temp import AuthGrpcEmailCodeServicerTemp
from .methods.nickname_temp import AuthGrpcNicknameServicerTemp
from .profiles.attrs_temp import AuthGrpcAttrsServicerTemp
from .profiles.profiles_temp import AuthGrpcProfilesServicerTemp
from .profiles.tags_temp import AuthGrpcTagsServicerTemp
from .sessions.attrs_temp import AuthGrpcSessionAttrsServicerTemp
from .sessions.presets_temp import AuthGrpcSessionPresetsServicerTemp
from .sessions.sessions_temp import AuthGrpcSessionsServicerTemp
from .sign_in_temp import AuthGrpcSignInServicerTemp
from .sign_out_temp import AuthGrpcSignOutServicerTemp
from .sign_up_temp import AuthGrpcSignUpServicerTemp


class AuthGrpcFlowsBinding(
    AuthGrpcSignUpBinding, AuthGrpcSignInBinding, AuthGrpcSignOutBinding
):
    """The answers of the flows, for the methods of more steps, and the sign-out."""


class AuthGrpcAdminBinding(
    AuthGrpcProfileRegistriesBinding,
    AuthGrpcProfilesBinding,
    AuthGrpcSessionRegistriesBinding,
    AuthGrpcSessionsBinding,
    AuthGrpcAccessBinding,
    AuthGrpcActivitiesBinding,
):
    pass
