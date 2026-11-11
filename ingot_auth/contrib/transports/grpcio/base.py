"""The base of the servicers."""

__all__ = ("BaseAuthGrpcServicer", "Context")

import typing as t

from grpc import aio
from ingot_grpcio.grpc.services import GrpcServicer
from ingots.defaults.operations import ANONYMOUS_CALLER, BaseOperation, Caller

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject

Context: t.TypeAlias = aio.ServicerContext[t.Any, t.Any]


class BaseAuthGrpcServicer(GrpcServicer):
    """
    A servicer of the auth: an RPC turns its request into the parameters of
    an operation and the result into its reply, nothing else. The operation
    runs for the caller of :meth:`_get_caller`; its exceptions reach the
    policies of :class:`~..errors.AuthGrpcErrorsUnit`.
    """

    project: "AuthProject"

    @t.final
    async def run_operation[ParametersType, ResultType](
        self,
        factory: "BoundFactory[BaseOperation[ParametersType, ResultType]]",
        parameters: ParametersType,
        context: Context,
    ) -> ResultType:
        """Runs an operation for the caller of a call."""
        operations = self.project.operations
        metadata = operations.create_metadata(await self._get_caller(context))
        return await operations.runner.run(factory, parameters, metadata)

    async def _get_caller(self, context: Context) -> Caller:
        """
        The caller of a call: that of the session of its token, ``Bearer
        <token>`` in the header ``authorization``, or the anonymous one with
        no token. A servicer open to anyone runs for the anonymous one,
        whatever the call bears.

        :raises AuthSessionNotFoundError: no open session has the token.
        :raises AuthSessionExpiredError: its session expired, closed now.
        """
        # the one way a call bears its credential for now, Bearer; it moves
        # into a strategy in a slot later (a cookie of gRPC-Web, mTLS, an API
        # key...), for an application to pick one or write its own, which
        # until then overrides this hook
        token = get_bearer_token(context.invocation_metadata())
        if token is None:
            return self._get_anonymous_caller()
        return await self.project.auth.sessions.authenticate(token)

    def _get_anonymous_caller(self) -> Caller:
        """
        The caller of a call that tells no one: with no permissions, so that
        it may do only what needs none, until a servicer open to anyone gives
        what anyone may.
        """
        return ANONYMOUS_CALLER


def get_bearer_token(
    metadata: "Iterable[tuple[str, str | bytes]] | None",
) -> str | None:
    """
    Internal: the token of the header ``authorization`` of a call, of the
    scheme ``Bearer`` in any case (RFC 6750), ``None`` without one: a header
    of another scheme tells no token either.
    """
    for key, value in metadata or ():
        if key == "authorization" and isinstance(value, str):
            scheme, _, token = value.partition(" ")
            if scheme.lower() == "bearer" and token.strip():
                return token.strip()
    return None
