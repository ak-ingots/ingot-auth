"""
The metadata of the auth: the registries and the methods, as its consumers
read them.
"""

__all__ = (
    "AuthGetMetadataOperation",
    "AuthMetadata",
    "AuthMetadataPermissions",
    "AuthMetadataUnit",
    "AuthMethodMetadata",
    "AuthProfileMetadata",
    "AuthSessionMetadata",
)

import typing as t

from ingots.defaults.operations import OperationsOwner, Permissions, PermissionsSlot
from ingots.puer import Factory, Unit

from .items import (
    AuthMetadata,
    AuthMethodMetadata,
    AuthProfileMetadata,
    AuthSessionMetadata,
)
from .operations import AuthGetMetadataOperation
from .permissions import AuthMetadataPermissions


class AuthMetadataUnit(OperationsOwner, Unit):
    """The operations of the metadata, open to anyone."""

    permissions = PermissionsSlot(AuthMetadataPermissions)

    op_get = Factory(AuthGetMetadataOperation)

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """
        What the metadata gives the anonymous caller: its ``CAN_READ``, as a
        client reads it before signing in.
        """
        return self.permissions(self.permissions.flags.CAN_READ)
