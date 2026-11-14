"""
The dispatcher in the process: an operation runs in a task of asyncio, lost
if the process stops before it ends. An application declares it in the slot
of its auth: ``dispatcher = Slot(AuthMemoryDispatcher)``.
"""

__all__ = ("AuthMemoryDispatcher",)

import asyncio
import typing as t

from ingot_auth.dispatchers import BaseAuthDispatcher

if t.TYPE_CHECKING:
    from ingots.defaults.operations import BaseOperation, OperationMetadata
    from ingots.puer import BoundFactory


class AuthMemoryDispatcher(BaseAuthDispatcher):
    """
    The operations run by the runner of the project, ``run_safe()``, in
    tasks of asyncio of the dispatcher, each held until it ends: a failure is
    logged by the runner, and fails nothing else.
    """

    def __init__(self) -> None:
        super().__init__()
        self._tasks: set[asyncio.Task[None]] = set()

    @t.final
    async def join(self) -> None:
        """
        Waits for the operations dispatched so far to end, and for those they
        dispatch: for a shutdown, a test.
        """
        # a task done leaves the set by a callback yet to run: awaiting done
        # tasks alone may not yield to it
        while pending := [task for task in self._tasks if not task.done()]:
            await asyncio.gather(*pending)

    @t.override
    async def _dispatch[ParametersType](
        self,
        factory: "BoundFactory[BaseOperation[ParametersType, None]]",
        parameters: ParametersType,
        metadata: "OperationMetadata",
    ) -> None:
        runner = self.project.operations.runner
        task = asyncio.create_task(runner.run_safe(factory, parameters, metadata))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
