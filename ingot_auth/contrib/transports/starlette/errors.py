"""
The problems of the exceptions of the auth over HTTP: the statuses of the
contract, as problems of RFC 9457.
"""

__all__ = (
    "AuthStarletteErrorsUnit",
    "AuthStarletteAttemptNotFoundPolicy",
    "AuthStarletteGroupNotFoundPolicy",
    "AuthStarletteIdentityConflictPolicy",
    "AuthStarletteItemConflictPolicy",
    "AuthStarletteItemInvalidPolicy",
    "AuthStarletteItemNotFoundPolicy",
    "AuthStarletteMethodDeniedPolicy",
    "AuthStarletteMethodInvalidPolicy",
    "AuthStarletteMethodNotFoundPolicy",
    "AuthStarletteMethodRefusedPolicy",
    "AuthStarletteMethodUnsupportedPolicy",
    "AuthStarletteOwnSessionNotFoundPolicy",
    "AuthStarlettePermissionsPolicy",
    "AuthStarletteProfileNotFoundPolicy",
    "AuthStarletteSessionExpiredPolicy",
    "AuthStarletteSessionNotFoundPolicy",
    "AuthStarletteSessionsLimitPolicy",
    "BaseAuthStarletteErrorPolicy",
)

import typing as t

from ingot_starlette.contrib.protobuf import get_http_status
from ingot_starlette.starlette.errors import (
    BaseStaticStarletteErrorPolicy,
    StarletteErrorsUnit,
)
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


class BaseAuthStarletteErrorPolicy(BaseAuthErrorMixin, BaseStaticStarletteErrorPolicy):
    """
    A policy of an exception of the auth over HTTP: the status of its mixin
    of the contract, of the status of HTTP of its code (AIP-193), its
    reason, domain and metadata as the extensions of the problem, as the
    ``ErrorInfo`` of gRPC tells them, for a client to tell them apart by
    ``reason``.
    """

    @t.override
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Any) -> None:
        if hasattr(cls, "RPC_CODE"):
            cls.STATUS = get_http_status(cls.RPC_CODE)
        super().__init_subclass__(**kwargs)

    @t.final
    @t.override
    def _get_extensions(self, error: Exception) -> t.Mapping[str, object]:
        return {
            "domain": self.DOMAIN,
            "reason": self.REASON,
            "metadata": self._get_error_metadata(error),
        }


class AuthStarletteItemConflictPolicy(
    AuthItemConflictErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteItemInvalidPolicy(
    AuthItemInvalidErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteItemNotFoundPolicy(
    AuthItemNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteGroupNotFoundPolicy(
    AuthGroupNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteProfileNotFoundPolicy(
    AuthProfileNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarlettePermissionsPolicy(
    AuthPermissionsErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteMethodNotFoundPolicy(
    AuthMethodNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteMethodRefusedPolicy(
    AuthMethodRefusedErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteMethodDeniedPolicy(
    AuthMethodDeniedErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteMethodInvalidPolicy(
    AuthMethodInvalidErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteMethodUnsupportedPolicy(
    AuthMethodUnsupportedErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteAttemptNotFoundPolicy(
    AuthAttemptNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteIdentityConflictPolicy(
    AuthIdentityConflictErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteSessionNotFoundPolicy(
    AuthSessionNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteSessionExpiredPolicy(
    AuthSessionExpiredErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteOwnSessionNotFoundPolicy(
    AuthOwnSessionNotFoundErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteSessionsLimitPolicy(
    AuthSessionsLimitErrorMixin, BaseAuthStarletteErrorPolicy
):
    pass


class AuthStarletteErrorsUnit(StarletteErrorsUnit):
    """
    The policies of the auth: the errors unit of Starlette takes it as a
    base, as that of gRPC takes ``AuthGrpcErrorsUnit``, the same statuses.
    """

    auth_item_conflict = Slot(AuthStarletteItemConflictPolicy)
    auth_item_invalid = Slot(AuthStarletteItemInvalidPolicy)
    auth_item_not_found = Slot(AuthStarletteItemNotFoundPolicy)
    auth_group_not_found = Slot(AuthStarletteGroupNotFoundPolicy)
    auth_profile_not_found = Slot(AuthStarletteProfileNotFoundPolicy)
    auth_permissions = Slot(AuthStarlettePermissionsPolicy)
    auth_method_not_found = Slot(AuthStarletteMethodNotFoundPolicy)
    auth_method_refused = Slot(AuthStarletteMethodRefusedPolicy)
    auth_method_denied = Slot(AuthStarletteMethodDeniedPolicy)
    auth_method_invalid = Slot(AuthStarletteMethodInvalidPolicy)
    auth_method_unsupported = Slot(AuthStarletteMethodUnsupportedPolicy)
    auth_attempt_not_found = Slot(AuthStarletteAttemptNotFoundPolicy)
    auth_identity_conflict = Slot(AuthStarletteIdentityConflictPolicy)
    auth_session_not_found = Slot(AuthStarletteSessionNotFoundPolicy)
    auth_session_expired = Slot(AuthStarletteSessionExpiredPolicy)
    auth_own_session_not_found = Slot(AuthStarletteOwnSessionNotFoundPolicy)
    auth_sessions_limit = Slot(AuthStarletteSessionsLimitPolicy)
