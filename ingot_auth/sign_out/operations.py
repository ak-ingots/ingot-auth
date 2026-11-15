"""The operation of the sign-out."""

__all__ = ("AuthSignOutOperation",)

import typing as t

from ingots.defaults.operations import BaseOperation, OperationMetadata, Permissions

from ingot_auth.caches import AuthCaller
from ingot_auth.storages import AuthSessionCloseReason, AuthSessionNotFoundError

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


class AuthSignOutOperation(BaseOperation[None, None]):
    """
    Closes the session of the caller, ``SIGNED_OUT``. Any caller may: one of
    no session, the root, the anonymous one, signs out of nothing, and of a
    session closed meanwhile too.
    """

    project: "AuthProject"

    @t.override
    def _get_permissions(self) -> Permissions:
        return Permissions()

    @t.override
    async def _run(self, parameters: None, metadata: OperationMetadata) -> None:
        caller = metadata.caller
        if not isinstance(caller, AuthCaller):
            return
        try:
            await self.project.auth.sessions.close(
                caller.uid, caller.session_id, AuthSessionCloseReason.SIGNED_OUT
            )
        except AuthSessionNotFoundError:
            pass  # closed meanwhile: nothing to tell
