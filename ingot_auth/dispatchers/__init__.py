"""
The dispatcher of the auth: the interface a backend in
``ingot_auth.contrib.dispatchers`` implements, which runs operations of the
auth in the background, the sending of a code by mail for one, so that a
step replies at once. The dispatcher in the process runs one in a task of
asyncio; one on a queue would serialize the path of its factory, its
parameters and its metadata for a worker running the same operation.
"""

__all__ = ("BaseAuthDispatcher",)

import abc
import typing as t

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingots.defaults.operations import BaseOperation, OperationMetadata
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class BaseAuthDispatcher(Entity):
    """
    The dispatcher of the operations of the auth run in the background, the
    slot ``dispatcher`` of the auth, abstract: what a backend implements.
    """

    project: "AuthProject"

    @t.final
    async def dispatch[ParametersType](
        self,
        factory: "BoundFactory[BaseOperation[ParametersType, None]]",
        parameters: ParametersType,
        metadata: "OperationMetadata",
    ) -> None:
        """
        Runs the operation ``factory`` creates in the background, with
        ``parameters`` for the caller of ``metadata``, returning before it
        ends: a failure is logged, and fails nothing else.
        """
        await self._dispatch(factory, parameters, metadata)

    @abc.abstractmethod
    async def _dispatch[ParametersType](
        self,
        factory: "BoundFactory[BaseOperation[ParametersType, None]]",
        parameters: ParametersType,
        metadata: "OperationMetadata",
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._dispatch")
