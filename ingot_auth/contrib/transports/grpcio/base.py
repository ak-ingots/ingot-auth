"""The base of the servicers."""

__all__ = ("BaseAuthGrpcServicer", "Context")

import typing as t

from grpc import aio
from ingot_grpcio.grpc.services import GrpcServicer
from ingots.defaults.operations import ANONYMOUS_CALLER, BaseOperation, Caller

if t.TYPE_CHECKING:
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
        metadata = operations.create_metadata(self._get_caller(context))
        return await operations.runner.run(factory, parameters, metadata)

    def _get_caller(self, context: Context) -> Caller:
        """
        The caller of a call: anonymous, so that a call may do only what
        needs no permissions, until a subclass tells who is calling.
        """
        return ANONYMOUS_CALLER
