"""
The errors of the auth as the statuses of its contract, of no transport: an
exception, its code of ``google.rpc.Code``, its reason and the metadata of
its ``ErrorInfo``, in the domain ``ingot-auth``. The policies of gRPC and of
HTTP mix them in, each its own form, so that both transports tell alike.
"""

__all__ = (
    "BaseAuthErrorMixin",
    "BaseAuthItemErrorMixin",
    "AuthAttemptNotFoundErrorMixin",
    "AuthGroupNotFoundErrorMixin",
    "AuthIdentityConflictErrorMixin",
    "AuthItemConflictErrorMixin",
    "AuthItemInvalidErrorMixin",
    "AuthItemNotFoundErrorMixin",
    "AuthMethodDeniedErrorMixin",
    "AuthMethodInvalidErrorMixin",
    "AuthMethodNotFoundErrorMixin",
    "AuthMethodRefusedErrorMixin",
    "AuthMethodUnsupportedErrorMixin",
    "AuthOwnSessionNotFoundErrorMixin",
    "AuthPermissionsErrorMixin",
    "AuthProfileNotFoundErrorMixin",
    "AuthSessionExpiredErrorMixin",
    "AuthSessionNotFoundErrorMixin",
    "AuthSessionsLimitErrorMixin",
)

import typing as t

from google.rpc import code_pb2
from ingots.defaults.operations import OperationPermissionsError

from ingot_auth.access.groups import AuthGroupError, AuthGroupNotFoundError
from ingot_auth.caches import AuthAttemptNotFoundError
from ingot_auth.methods import (
    AuthMethodDeniedError,
    AuthMethodInvalidError,
    AuthMethodNotFoundError,
    AuthMethodRefusedError,
    AuthMethodUnsupportedError,
)
from ingot_auth.registry import AuthItemInvalidError
from ingot_auth.sessions import (
    AuthOwnSessionNotFoundError,
    AuthSessionExpiredError,
    AuthSessionsLimitError,
)
from ingot_auth.storages import (
    AuthIdentityConflictError,
    AuthIdentityError,
    AuthItemConflictError,
    AuthItemNotFoundError,
    AuthProfileError,
    AuthProfileNotFoundError,
    AuthRegistryError,
    AuthSessionNotFoundError,
)


class BaseAuthErrorMixin:
    """
    The status of an exception of the auth, of :attr:`EXCEPTION` and its
    subclasses: :attr:`RPC_CODE` of ``google.rpc.Code``, :attr:`REASON`, in
    :attr:`DOMAIN`, the metadata of :meth:`_get_error_metadata`.
    """

    EXCEPTION: t.ClassVar[type[Exception]]
    RPC_CODE: t.ClassVar[int]
    REASON: t.ClassVar[str]
    DOMAIN: t.ClassVar[str] = "ingot-auth"

    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        """The metadata of the status: none here."""
        return {}


class BaseAuthItemErrorMixin(BaseAuthErrorMixin):
    """A status of a registry: tells the registry and the key in question."""

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        registry_error = t.cast(AuthRegistryError, error)
        return {"registry": registry_error.registry, "key": str(registry_error.key)}


class AuthItemConflictErrorMixin(BaseAuthItemErrorMixin):
    EXCEPTION: t.ClassVar[type[Exception]] = AuthItemConflictError
    RPC_CODE = code_pb2.ALREADY_EXISTS
    REASON = "ITEM_CONFLICT"


class AuthItemInvalidErrorMixin(BaseAuthItemErrorMixin):
    EXCEPTION: t.ClassVar[type[Exception]] = AuthItemInvalidError
    RPC_CODE = code_pb2.INVALID_ARGUMENT
    REASON = "ITEM_INVALID"


class AuthItemNotFoundErrorMixin(BaseAuthItemErrorMixin):
    EXCEPTION: t.ClassVar[type[Exception]] = AuthItemNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "ITEM_NOT_FOUND"


class AuthGroupNotFoundErrorMixin(BaseAuthErrorMixin):
    """No group has the name: tells it."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthGroupNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "GROUP_NOT_FOUND"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"group": t.cast(AuthGroupError, error).name}


class AuthProfileNotFoundErrorMixin(BaseAuthErrorMixin):
    """No profile has the uid: tells it, to the administration it is for."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthProfileNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "PROFILE_NOT_FOUND"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"uid": t.cast(AuthProfileError, error).uid}


class AuthPermissionsErrorMixin(BaseAuthErrorMixin):
    EXCEPTION: t.ClassVar[type[Exception]] = OperationPermissionsError
    RPC_CODE = code_pb2.PERMISSION_DENIED
    REASON = "PERMISSION_DENIED"


class AuthMethodNotFoundErrorMixin(BaseAuthErrorMixin):
    """No method has the name: tells it."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthMethodNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "METHOD_NOT_FOUND"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"method": t.cast(AuthMethodNotFoundError, error).name}


class AuthMethodRefusedErrorMixin(BaseAuthErrorMixin):
    """
    The method refuses what it is given, a wrong secret or no such user
    alike: tells nothing more.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthMethodRefusedError
    RPC_CODE = code_pb2.UNAUTHENTICATED
    REASON = "METHOD_REFUSED"


class AuthMethodDeniedErrorMixin(BaseAuthErrorMixin):
    """The profile may not sign in by the method: tells the method."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthMethodDeniedError
    RPC_CODE = code_pb2.PERMISSION_DENIED
    REASON = "METHOD_DENIED"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"method": t.cast(AuthMethodDeniedError, error).name}


class AuthMethodInvalidErrorMixin(BaseAuthErrorMixin):
    """
    A field breaks policies of the method: tells the field and the policies,
    separated by commas, in the order of their group.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthMethodInvalidError
    RPC_CODE = code_pb2.INVALID_ARGUMENT
    REASON = "METHOD_INVALID"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        invalid = t.cast(AuthMethodInvalidError, error)
        return {"field": invalid.field, "policies": ",".join(invalid.policies)}


class AuthMethodUnsupportedErrorMixin(BaseAuthErrorMixin):
    """The method takes no part in the flow: tells the flow."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthMethodUnsupportedError
    RPC_CODE = code_pb2.FAILED_PRECONDITION
    REASON = "METHOD_UNSUPPORTED"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"flow": t.cast(AuthMethodUnsupportedError, error).flow}


class AuthAttemptNotFoundErrorMixin(BaseAuthErrorMixin):
    """
    No attempt waits under the id of an answer: none was, it expired, it is
    over, or it is of another flow. The client starts again.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthAttemptNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "ATTEMPT_NOT_FOUND"


class AuthIdentityConflictErrorMixin(BaseAuthErrorMixin):
    """
    The identifier is bound already, told on a sign-up as the user picks
    another: tells its kind, never the identifier.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthIdentityConflictError
    RPC_CODE = code_pb2.ALREADY_EXISTS
    REASON = "IDENTITY_CONFLICT"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"kind": t.cast(AuthIdentityError, error).kind}


class AuthSessionNotFoundErrorMixin(BaseAuthErrorMixin):
    """
    No open session has the token of a call: the client signs in again. Tells
    nothing of the token.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthSessionNotFoundError
    RPC_CODE = code_pb2.UNAUTHENTICATED
    REASON = "SESSION_NOT_FOUND"


class AuthSessionExpiredErrorMixin(BaseAuthErrorMixin):
    """The session of the token of a call expired: tells the reason it closed."""

    EXCEPTION: t.ClassVar[type[Exception]] = AuthSessionExpiredError
    RPC_CODE = code_pb2.UNAUTHENTICATED
    REASON = "SESSION_EXPIRED"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"reason": t.cast(AuthSessionExpiredError, error).reason.value}


class AuthOwnSessionNotFoundErrorMixin(BaseAuthErrorMixin):
    """
    No open session of the caller has the id: its own, closed or never one,
    or of another. The caller stays signed in, the session is not found.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthOwnSessionNotFoundError
    RPC_CODE = code_pb2.NOT_FOUND
    REASON = "OWN_SESSION_NOT_FOUND"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"session_uid": t.cast(AuthOwnSessionNotFoundError, error).session_uid}


class AuthSessionsLimitErrorMixin(BaseAuthErrorMixin):
    """
    A sign-in refused over the limit of the sessions of the profile: the user
    signs out of another first. Tells how many are open.
    """

    EXCEPTION: t.ClassVar[type[Exception]] = AuthSessionsLimitError
    RPC_CODE = code_pb2.RESOURCE_EXHAUSTED
    REASON = "SESSIONS_LIMIT"

    @t.override
    def _get_error_metadata(self, error: Exception) -> dict[str, str]:
        return {"count": str(t.cast(AuthSessionsLimitError, error).count)}
