"""The statuses of the exceptions of the auth."""

__all__ = (
    "AuthGrpcAttemptNotFoundPolicy",
    "AuthGrpcErrorsUnit",
    "AuthGrpcGroupNotFoundPolicy",
    "AuthGrpcIdentityConflictPolicy",
    "AuthGrpcItemConflictPolicy",
    "AuthGrpcItemInvalidPolicy",
    "AuthGrpcItemNotFoundPolicy",
    "AuthGrpcMethodDeniedPolicy",
    "AuthGrpcMethodInvalidPolicy",
    "AuthGrpcMethodNotFoundPolicy",
    "AuthGrpcMethodRefusedPolicy",
    "AuthGrpcMethodUnsupportedPolicy",
    "AuthGrpcPermissionsPolicy",
    "AuthGrpcProfileNotFoundPolicy",
    "AuthGrpcSessionExpiredPolicy",
    "AuthGrpcSessionNotFoundPolicy",
    "BaseAuthGrpcErrorPolicy",
    "BaseAuthGrpcItemPolicy",
)

import typing as t

import grpc
from ingot_grpcio.grpc.errors import BaseStaticGrpcErrorPolicy, GrpcErrorsUnit
from ingots.defaults.operations import OperationPermissionsError
from ingots.puer import Slot

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
from ingot_auth.sessions import AuthSessionExpiredError
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


class BaseAuthGrpcErrorPolicy(BaseStaticGrpcErrorPolicy):
    """A policy of an exception of the auth: of the domain of the addon."""

    DOMAIN = "ingot-auth"


class BaseAuthGrpcItemPolicy(BaseAuthGrpcErrorPolicy):
    """A policy of a registry: tells the registry and the key in question."""

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        registry_error = t.cast(AuthRegistryError, error)
        return {"registry": registry_error.registry, "key": str(registry_error.key)}


class AuthGrpcItemConflictPolicy(BaseAuthGrpcItemPolicy):
    EXCEPTION = AuthItemConflictError
    CODE = grpc.StatusCode.ALREADY_EXISTS
    REASON = "ITEM_CONFLICT"


class AuthGrpcItemInvalidPolicy(BaseAuthGrpcItemPolicy):
    EXCEPTION = AuthItemInvalidError
    CODE = grpc.StatusCode.INVALID_ARGUMENT
    REASON = "ITEM_INVALID"


class AuthGrpcItemNotFoundPolicy(BaseAuthGrpcItemPolicy):
    EXCEPTION = AuthItemNotFoundError
    CODE = grpc.StatusCode.NOT_FOUND
    REASON = "ITEM_NOT_FOUND"


class AuthGrpcGroupNotFoundPolicy(BaseAuthGrpcErrorPolicy):
    """No group has the name: tells it."""

    EXCEPTION = AuthGroupNotFoundError
    CODE = grpc.StatusCode.NOT_FOUND
    REASON = "GROUP_NOT_FOUND"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"group": t.cast(AuthGroupError, error).name}


class AuthGrpcProfileNotFoundPolicy(BaseAuthGrpcErrorPolicy):
    """No profile has the uid: tells it, to the administration it is for."""

    EXCEPTION = AuthProfileNotFoundError
    CODE = grpc.StatusCode.NOT_FOUND
    REASON = "PROFILE_NOT_FOUND"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"uid": t.cast(AuthProfileError, error).uid}


class AuthGrpcPermissionsPolicy(BaseAuthGrpcErrorPolicy):
    EXCEPTION = OperationPermissionsError
    CODE = grpc.StatusCode.PERMISSION_DENIED
    REASON = "PERMISSION_DENIED"


class AuthGrpcMethodNotFoundPolicy(BaseAuthGrpcErrorPolicy):
    """No method has the name: tells it."""

    EXCEPTION = AuthMethodNotFoundError
    CODE = grpc.StatusCode.NOT_FOUND
    REASON = "METHOD_NOT_FOUND"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"method": t.cast(AuthMethodNotFoundError, error).name}


class AuthGrpcMethodRefusedPolicy(BaseAuthGrpcErrorPolicy):
    """
    The method refuses what it is given, a wrong secret or no such user
    alike: tells nothing more.
    """

    EXCEPTION = AuthMethodRefusedError
    CODE = grpc.StatusCode.UNAUTHENTICATED
    REASON = "METHOD_REFUSED"


class AuthGrpcMethodDeniedPolicy(BaseAuthGrpcErrorPolicy):
    """The profile may not sign in by the method: tells the method."""

    EXCEPTION = AuthMethodDeniedError
    CODE = grpc.StatusCode.PERMISSION_DENIED
    REASON = "METHOD_DENIED"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"method": t.cast(AuthMethodDeniedError, error).name}


class AuthGrpcMethodInvalidPolicy(BaseAuthGrpcErrorPolicy):
    """
    A field breaks policies of the method: tells the field and the policies,
    separated by commas, in the order of their group.
    """

    EXCEPTION = AuthMethodInvalidError
    CODE = grpc.StatusCode.INVALID_ARGUMENT
    REASON = "METHOD_INVALID"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        invalid = t.cast(AuthMethodInvalidError, error)
        return {"field": invalid.field, "policies": ",".join(invalid.policies)}


class AuthGrpcMethodUnsupportedPolicy(BaseAuthGrpcErrorPolicy):
    """The method takes no part in the flow: tells the flow."""

    EXCEPTION = AuthMethodUnsupportedError
    CODE = grpc.StatusCode.FAILED_PRECONDITION
    REASON = "METHOD_UNSUPPORTED"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"flow": t.cast(AuthMethodUnsupportedError, error).flow}


class AuthGrpcAttemptNotFoundPolicy(BaseAuthGrpcErrorPolicy):
    """
    No attempt waits under the id of an answer: none was, it expired, it is
    over, or it is of another flow. The client starts again.
    """

    EXCEPTION = AuthAttemptNotFoundError
    CODE = grpc.StatusCode.NOT_FOUND
    REASON = "ATTEMPT_NOT_FOUND"


class AuthGrpcIdentityConflictPolicy(BaseAuthGrpcErrorPolicy):
    """
    The identifier is bound already, told on a sign-up as the user picks
    another: tells its kind, never the identifier.
    """

    EXCEPTION = AuthIdentityConflictError
    CODE = grpc.StatusCode.ALREADY_EXISTS
    REASON = "IDENTITY_CONFLICT"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"kind": t.cast(AuthIdentityError, error).kind}


class AuthGrpcSessionNotFoundPolicy(BaseAuthGrpcErrorPolicy):
    """
    No open session has the token of a call: the client signs in again. Tells
    nothing of the token.
    """

    EXCEPTION = AuthSessionNotFoundError
    CODE = grpc.StatusCode.UNAUTHENTICATED
    REASON = "SESSION_NOT_FOUND"


class AuthGrpcSessionExpiredPolicy(BaseAuthGrpcErrorPolicy):
    """The session of the token of a call expired: tells the reason it closed."""

    EXCEPTION = AuthSessionExpiredError
    CODE = grpc.StatusCode.UNAUTHENTICATED
    REASON = "SESSION_EXPIRED"

    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return {"reason": t.cast(AuthSessionExpiredError, error).reason.value}


class AuthGrpcErrorsUnit(GrpcErrorsUnit):
    """The policies of the auth: the errors unit of the gRPC takes it as a base."""

    auth_item_conflict = Slot(AuthGrpcItemConflictPolicy)
    auth_item_invalid = Slot(AuthGrpcItemInvalidPolicy)
    auth_item_not_found = Slot(AuthGrpcItemNotFoundPolicy)
    auth_group_not_found = Slot(AuthGrpcGroupNotFoundPolicy)
    auth_profile_not_found = Slot(AuthGrpcProfileNotFoundPolicy)
    auth_permissions = Slot(AuthGrpcPermissionsPolicy)
    auth_method_not_found = Slot(AuthGrpcMethodNotFoundPolicy)
    auth_method_refused = Slot(AuthGrpcMethodRefusedPolicy)
    auth_method_denied = Slot(AuthGrpcMethodDeniedPolicy)
    auth_method_invalid = Slot(AuthGrpcMethodInvalidPolicy)
    auth_method_unsupported = Slot(AuthGrpcMethodUnsupportedPolicy)
    auth_attempt_not_found = Slot(AuthGrpcAttemptNotFoundPolicy)
    auth_identity_conflict = Slot(AuthGrpcIdentityConflictPolicy)
    auth_session_not_found = Slot(AuthGrpcSessionNotFoundPolicy)
    auth_session_expired = Slot(AuthGrpcSessionExpiredPolicy)
