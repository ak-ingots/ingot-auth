"""The sign-out as messages: the RPC of its service, of no transport."""

__all__ = ("AuthSignOutRpcMixin",)

import typing as t

from ingot_auth.sessions import AuthSessionExpiredError
from ingot_auth.storages import AuthSessionNotFoundError

from ..base import AuthSessionRpcMixin
from .v1 import sign_out_pb2

if t.TYPE_CHECKING:
    from ingots.defaults.operations import Caller

    from ..context import BaseAuthRpcContext


class AuthSignOutRpcMixin(AuthSessionRpcMixin):
    """
    The sign-out of the caller of the token of a call, open to any caller: a
    token closed, expired or unknown gives the anonymous one, which signs out
    of nothing, so that a client may retry and learns nothing.
    """

    @t.final
    async def rpc_sign_out(
        self, request: sign_out_pb2.SignOutRequest, context: "BaseAuthRpcContext"
    ) -> sign_out_pb2.SignOutResponse:
        factory = self.project.auth.sign_out.op_sign_out
        await self.rpc_run_operation(factory, None, context)
        return sign_out_pb2.SignOutResponse()

    @t.override
    async def _rpc_get_caller(self, context: "BaseAuthRpcContext") -> "Caller":
        try:
            return await super()._rpc_get_caller(context)
        except AuthSessionNotFoundError, AuthSessionExpiredError:
            return self.project.operations.callers.get_anonymous()
