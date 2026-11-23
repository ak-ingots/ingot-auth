"""
The auth as the messages of its contract, of no transport: the RPCs of its
services as mixins, each turning a request into the parameters of an
operation and its result into the reply, run for the caller a context of a
call tells; the servicers of gRPC and the endpoints of HTTP mix them in,
each adapting its own context, so that both transports answer alike. It
needs protobuf alone, no grpcio.
"""

__all__ = (
    "PROFILE_HASH_KEY",
    "AuthEmailCodeRpcMixin",
    "AuthMetadataRpcMixin",
    "AuthNicknameRpcMixin",
    "AuthProfilesRpcMixin",
    "AuthRpcMixin",
    "AuthSessionRpcMixin",
    "AuthSessionsRpcMixin",
    "AuthSignInRpcMixin",
    "AuthSignOutRpcMixin",
    "AuthSignUpRpcMixin",
    "BaseAuthMethodRpcMixin",
    "BaseAuthRpcContext",
    "parse_bearer_token",
)

from .base import (
    PROFILE_HASH_KEY,
    AuthRpcMixin,
    AuthSessionRpcMixin,
    parse_bearer_token,
)
from .context import BaseAuthRpcContext
from .metadata.rpcs import AuthMetadataRpcMixin
from .methods.base import BaseAuthMethodRpcMixin
from .methods.email_code.rpcs import AuthEmailCodeRpcMixin
from .methods.nickname.rpcs import AuthNicknameRpcMixin
from .profiles.rpcs import AuthProfilesRpcMixin
from .sessions.rpcs import AuthSessionsRpcMixin
from .sign_in.rpcs import AuthSignInRpcMixin
from .sign_out.rpcs import AuthSignOutRpcMixin
from .sign_up.rpcs import AuthSignUpRpcMixin
