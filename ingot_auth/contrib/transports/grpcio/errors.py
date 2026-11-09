"""The statuses of the exceptions of the auth."""

__all__ = (
    "AuthGrpcErrors",
    "AuthGrpcGroupNotFoundPolicy",
    "AuthGrpcItemConflictPolicy",
    "AuthGrpcItemInvalidPolicy",
    "AuthGrpcItemNotFoundPolicy",
    "AuthGrpcPermissionsPolicy",
    "AuthGrpcProfileNotFoundPolicy",
    "BaseAuthGrpcErrorPolicy",
    "BaseAuthGrpcItemPolicy",
)

import typing as t

import grpc
from ingot_grpcio.grpc.errors import BaseStaticGrpcErrorPolicy, GrpcErrors
from ingots.defaults.operations import OperationPermissionsError
from ingots.puer import Slot

from ingot_auth.access.groups import AuthGroupError, AuthGroupNotFoundError
from ingot_auth.profiles import AuthProfileError, AuthProfileNotFoundError
from ingot_auth.registry import (
    AuthItemConflictError,
    AuthItemInvalidError,
    AuthItemNotFoundError,
    AuthRegistryError,
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


class AuthGrpcErrors(GrpcErrors):
    """The policies of the auth: the errors unit of the gRPC takes it as a base."""

    auth_item_conflict = Slot(AuthGrpcItemConflictPolicy)
    auth_item_invalid = Slot(AuthGrpcItemInvalidPolicy)
    auth_item_not_found = Slot(AuthGrpcItemNotFoundPolicy)
    auth_group_not_found = Slot(AuthGrpcGroupNotFoundPolicy)
    auth_profile_not_found = Slot(AuthGrpcProfileNotFoundPolicy)
    auth_permissions = Slot(AuthGrpcPermissionsPolicy)
