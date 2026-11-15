"""
The metadata of the auth: the registries and the methods, as its consumers
read them.
"""

__all__ = (
    "AuthGetMetadataOperation",
    "AuthMetadata",
    "AuthMetadataUnit",
    "AuthMethodMetadata",
    "AuthProfileMetadata",
    "AuthSessionMetadata",
)

import typing as t

from ingots.defaults.operations import (
    OperationsOwner,
    PermissionFlags,
    Permissions,
    PermissionsSlot,
)
from ingots.puer import Factory, Unit

from .items import (
    AuthMetadata,
    AuthMethodMetadata,
    AuthProfileMetadata,
    AuthSessionMetadata,
)
from .operations import AuthGetMetadataOperation


class AuthMetadataUnit(OperationsOwner, Unit):
    """The operations of the metadata, open to anyone."""

    class Flags(PermissionFlags):
        """The operations on the metadata."""

        CAN_READ = 1 << 0

    permissions = PermissionsSlot(Flags)

    op_get = Factory(AuthGetMetadataOperation)

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """
        What the metadata gives the anonymous caller: its ``CAN_READ``, as a
        client reads it before signing in.
        """
        return self.permissions(self.permissions.flags.CAN_READ)
