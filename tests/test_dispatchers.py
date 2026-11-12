import typing as t
import unittest
from dataclasses import dataclass, field
from unittest import mock

from ingots.defaults.operations import (
    ROOT_CALLER,
    BaseOperation,
    OperationMetadata,
    Permissions,
)
from ingots.puer import Factory, Slot

from ingot_auth.__main__ import AuthMemoryProject, AuthMemoryUnit
from ingot_auth.contrib.dispatchers.memory import AuthMemoryDispatcher
from ingot_auth.project import AuthProject


@dataclass(frozen=True, slots=True, kw_only=True)
class Record:
    """A name to record in the list, then the records after it."""

    name: str
    done: list[str] = field(repr=False)
    then: tuple["Record", ...] = ()


class RecordOperation(BaseOperation[Record, None]):
    """Records the name, then dispatches the records after it."""

    PERMISSIONS = Permissions()

    project: "TstProject"

    @t.override
    async def _run(self, parameters: Record, metadata: OperationMetadata) -> None:
        if parameters.name == "failing":
            raise OSError(parameters.name)
        parameters.done.append(parameters.name)
        auth = self.project.auth
        for record in parameters.then:
            await auth.dispatcher.dispatch(auth.op_record, record, metadata)


class TstAuthUnit(AuthMemoryUnit):
    op_record = Factory(RecordOperation)


class TstProject(AuthMemoryProject):
    auth = Slot(TstAuthUnit)


class MemoryDispatcherTestCase(unittest.IsolatedAsyncioTestCase):
    @t.override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.logger = self.enterContext(
            mock.patch("ingots.defaults.operations.runner.logger")
        )
        self.project = TstProject()
        self.dispatcher = self.project.auth.dispatcher
        self.metadata = self.project.operations.create_metadata(ROOT_CALLER)
        self.done: list[str] = []

    async def dispatch(self, record: Record) -> None:
        auth = self.project.auth
        await self.dispatcher.dispatch(auth.op_record, record, self.metadata)

    def test_the_auth_in_memory_dispatches_in_the_process(self) -> None:
        project: AuthProject = AuthMemoryProject()
        self.assertIsInstance(project.auth.dispatcher, AuthMemoryDispatcher)

    async def test_an_operation_runs_after_its_dispatch_returns(self) -> None:
        await self.dispatch(Record(name="a", done=self.done))
        self.assertEqual(self.done, [])
        await self.dispatcher.join()
        self.assertEqual(self.done, ["a"])

    async def test_the_operations_one_dispatches_are_waited_for_too(self) -> None:
        last = Record(name="c", done=self.done)
        then = Record(name="b", done=self.done, then=(last,))
        await self.dispatch(Record(name="a", done=self.done, then=(then,)))
        await self.dispatcher.join()
        self.assertEqual(self.done, ["a", "b", "c"])

    async def test_an_operation_failing_is_logged_and_fails_nothing_else(
        self,
    ) -> None:
        for name in ("failing", "a"):
            await self.dispatch(Record(name=name, done=self.done))
        await self.dispatcher.join()
        self.assertEqual(self.done, ["a"])
        [call] = self.logger.warning.call_args_list
        self.assertEqual(call.args[1], "RecordOperation")
        self.assertIsInstance(call.args[2], OSError)
