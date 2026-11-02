"""The operations of the metadata."""

__all__ = ("AuthGetMetadata",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.session.attrs import AuthSessionAttrSource

from .items import AuthMetadata, AuthProfileMetadata, AuthSessionMetadata
from .permissions import AuthMetadataPermissions

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthGetMetadata(BaseOperation[None, AuthMetadata]):
    """
    The metadata: a client asks for it before signing in. Of the sessions it
    gives only what is the client's: the attributes the transport, the
    provider or the server give are not, nor are their bindings.
    """

    PERMISSIONS = Permissions(AuthMetadataPermissions.CAN_READ)

    project: "AuthProject"

    @t.override
    async def _run(self, parameters: None, metadata: OperationMetadata) -> AuthMetadata:
        return AuthMetadata(
            profile=await self._get_profile(), session=await self._get_session()
        )

    async def _get_profile(self) -> AuthProfileMetadata:
        storage = self.project.auth.storage.profile
        return AuthProfileMetadata(
            tags=await storage.tags.get_all(), attrs=await storage.attrs.get_all()
        )

    async def _get_session(self) -> AuthSessionMetadata:
        storage = self.project.auth.storage.session
        attrs = tuple(
            attr
            for attr in await storage.attrs.get_all()
            if attr.source is AuthSessionAttrSource.CLIENT
        )
        attr_ids = {attr.id for attr in attrs}
        bindings = await storage.presets.get_bindings()
        return AuthSessionMetadata(
            attrs=attrs,
            presets=await storage.presets.get_all(),
            bindings=tuple(b for b in bindings if b.attr_id in attr_ids),
        )
