"""The RPCs of the password of the profile of the caller."""

__all__ = ("AuthPasswordRpcMixin",)

import typing as t

from ingot_auth.methods.password import AuthChangePasswordParameters

from ...base import AuthSessionRpcMixin
from .v1 import password_pb2

if t.TYPE_CHECKING:
    from ingot_auth.api.context import BaseAuthRpcContext


class AuthPasswordRpcMixin(AuthSessionRpcMixin):
    """The change of the password of the caller, in the session of its token."""

    @t.final
    async def rpc_change_password(
        self,
        request: password_pb2.ChangePasswordRequest,
        context: "BaseAuthRpcContext",
    ) -> password_pb2.ChangePasswordResponse:
        parameters = AuthChangePasswordParameters(
            old=request.old_password, new=request.new_password
        )
        factory = self.project.auth.methods.password.op_change
        result = await self.rpc_run_operation(factory, parameters, context)
        return password_pb2.ChangePasswordResponse(revoked_count=result.revoked)
