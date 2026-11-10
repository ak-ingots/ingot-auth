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
    """The operations of the metadata."""

    op_get = Factory(AuthGetMetadataOperation)
