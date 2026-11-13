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

from ingots.defaults.operations import Permissions
from ingots.puer import Factory, Unit

from .items import (
    AuthMetadata,
    AuthMethodMetadata,
    AuthProfileMetadata,
    AuthSessionMetadata,
)
from .operations import AuthGetMetadataOperation
from .permissions import AuthMetadataPermissions


class AuthMetadataUnit(Unit):
    """The operations of the metadata, open to anyone."""

    op_get = Factory(AuthGetMetadataOperation)

    @t.final
    def get_anonymous_permissions(self) -> Permissions:
        """
        What the metadata gives the anonymous caller: its ``CAN_READ``, as a
        client reads it before signing in.
        """
        return Permissions(AuthMetadataPermissions.CAN_READ)
