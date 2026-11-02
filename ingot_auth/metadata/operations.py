"""The operations of the metadata."""

__all__ = ("AuthGetMetadata",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from .items import AuthMetadata
from .permissions import AuthMetadataPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGetMetadata(BaseOperation[None, AuthMetadata]):
    """The metadata: a client asks for it before signing in."""

    PERMISSIONS = Permissions(AuthMetadataPermissions.CAN_READ)

    project: "AuthProject"

    @t.override
    async def _run(self, parameters: None, metadata: OperationMetadata) -> AuthMetadata:
        storage = self.project.auth.storage
        return AuthMetadata(
            tags=await storage.profile.tags.get_all(),
            attrs=await storage.profile.attrs.get_all(),
        )
