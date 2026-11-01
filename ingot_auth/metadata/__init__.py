"""The metadata of the auth: the registries, as its consumers read them."""

__all__ = (
    "AuthGetMetadata",
    "AuthMetadata",
    "AuthMetadataPermissions",
    "AuthMetadataUnit",
)

from ingots.puer import Factory, Unit

from .items import AuthMetadata
from .operations import AuthGetMetadata
from .permissions import AuthMetadataPermissions


class AuthMetadataUnit(Unit):
    """The operations of the metadata."""

    op_get = Factory(AuthGetMetadata)
