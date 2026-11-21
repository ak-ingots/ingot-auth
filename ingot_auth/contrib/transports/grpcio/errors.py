"""The statuses of the exceptions of the auth, over gRPC: those of the contract."""

__all__ = (
    "AuthGrpcErrorsUnit",
    "AuthGrpcAttemptNotFoundPolicy",
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
    "AuthGrpcOwnSessionNotFoundPolicy",
    "AuthGrpcPermissionsPolicy",
    "AuthGrpcProfileNotFoundPolicy",
    "AuthGrpcSessionExpiredPolicy",
    "AuthGrpcSessionNotFoundPolicy",
    "AuthGrpcSessionsLimitPolicy",
    "BaseAuthGrpcErrorPolicy",
)

import typing as t

import grpc
from ingot_grpcio.grpc.errors import BaseStaticGrpcErrorPolicy, GrpcErrorsUnit
from ingots.puer import Slot

from ..contract.errors import (
    AuthAttemptNotFoundErrorMixin,
    AuthGroupNotFoundErrorMixin,
    AuthIdentityConflictErrorMixin,
    AuthItemConflictErrorMixin,
    AuthItemInvalidErrorMixin,
    AuthItemNotFoundErrorMixin,
    AuthMethodDeniedErrorMixin,
    AuthMethodInvalidErrorMixin,
    AuthMethodNotFoundErrorMixin,
    AuthMethodRefusedErrorMixin,
    AuthMethodUnsupportedErrorMixin,
    AuthOwnSessionNotFoundErrorMixin,
    AuthPermissionsErrorMixin,
    AuthProfileNotFoundErrorMixin,
    AuthSessionExpiredErrorMixin,
    AuthSessionNotFoundErrorMixin,
    AuthSessionsLimitErrorMixin,
    BaseAuthErrorMixin,
)

# the codes of gRPC by their numbers, those of google.rpc.Code
_GRPC_CODES: t.Final = {code.value[0]: code for code in grpc.StatusCode}


class BaseAuthGrpcErrorPolicy(BaseAuthErrorMixin, BaseStaticGrpcErrorPolicy):
    """
    A policy of an exception of the auth over gRPC: the status of its
    mixin of the contract, its code that of gRPC of the same number.
    """

    @t.override
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        if hasattr(cls, "RPC_CODE"):
            cls.CODE = _GRPC_CODES[cls.RPC_CODE]
        super().__init_subclass__(**kwargs)

    @t.final
    @t.override
    def _get_metadata(self, error: Exception) -> dict[str, str]:
        return self._get_error_metadata(error)


class AuthGrpcItemConflictPolicy(AuthItemConflictErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcItemInvalidPolicy(AuthItemInvalidErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcItemNotFoundPolicy(AuthItemNotFoundErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcGroupNotFoundPolicy(AuthGroupNotFoundErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcProfileNotFoundPolicy(
    AuthProfileNotFoundErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcPermissionsPolicy(AuthPermissionsErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcMethodNotFoundPolicy(
    AuthMethodNotFoundErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcMethodRefusedPolicy(AuthMethodRefusedErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcMethodDeniedPolicy(AuthMethodDeniedErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcMethodInvalidPolicy(AuthMethodInvalidErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


class AuthGrpcMethodUnsupportedPolicy(
    AuthMethodUnsupportedErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcAttemptNotFoundPolicy(
    AuthAttemptNotFoundErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcIdentityConflictPolicy(
    AuthIdentityConflictErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcSessionNotFoundPolicy(
    AuthSessionNotFoundErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcSessionExpiredPolicy(
    AuthSessionExpiredErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcOwnSessionNotFoundPolicy(
    AuthOwnSessionNotFoundErrorMixin, BaseAuthGrpcErrorPolicy
):
    pass


class AuthGrpcSessionsLimitPolicy(AuthSessionsLimitErrorMixin, BaseAuthGrpcErrorPolicy):
    pass


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
    auth_own_session_not_found = Slot(AuthGrpcOwnSessionNotFoundPolicy)
    auth_sessions_limit = Slot(AuthGrpcSessionsLimitPolicy)
