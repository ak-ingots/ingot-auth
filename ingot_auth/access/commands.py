"""The base of the commands of the access: its operations run by the operator."""

__all__ = ("BaseAuthAccessCommand",)

import abc
import typing as t

from ingots.defaults.operations import ROOT_CALLER, BaseOperation
from ingots.puer.cli import BaseCommand

if t.TYPE_CHECKING:
    from ingots.puer import BoundFactory

    from ingot_auth.project import AuthProject


class BaseAuthAccessCommand[ParametersType, ResultType](BaseCommand):
    """
    A command of the access: runs its operation, which a subclass gives in
    :meth:`_get_operation`, as the root, so that the first administrator is
    made here, before any caller may grant anything.
    """

    project: "AuthProject"

    @t.final
    async def run_operation(self, parameters: ParametersType) -> ResultType:
        """Runs the operation of the command as the root."""
        operations = self.project.operations
        metadata = operations.create_metadata(ROOT_CALLER)
        factory = self._get_operation()
        return await operations.runner.run(factory, parameters, metadata)

    @abc.abstractmethod
    def _get_operation(
        self,
    ) -> "BoundFactory[BaseOperation[ParametersType, ResultType]]":
        """The operation of the command: ``self.project.auth.access.groups.op_list``."""
        raise NotImplementedError(f"{type(self).__qualname__}._get_operation")
