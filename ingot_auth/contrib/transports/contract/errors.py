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

from ingot_auth.api.errors import (
    BaseAuthErrorMixin,
    BaseAuthItemErrorMixin,
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
)
