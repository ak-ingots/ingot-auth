"""The strategies of a failure to write the activity log."""

__all__ = (
    "AuthStrictActivityFailure",
    "AuthSwallowActivityFailure",
    "BaseAuthActivityFailure",
)

import abc
import logging
import typing as t

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from ingot_auth.storages import AuthActivityRecord

logger = logging.getLogger(__name__)


class BaseAuthActivityFailure(Entity):
    """
    What a failure to write a record of the log does, in the slot ``failure``
    of the log, which the application declares: it fails the change, or it
    is logged and the change goes through.
    """

    @t.final
    def handle(self, error: Exception, record: "AuthActivityRecord") -> None:
        """Handles the error of the storage appending the record."""
        self._handle(error, record)

    @abc.abstractmethod
    def _handle(self, error: Exception, record: "AuthActivityRecord") -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._handle")


class AuthStrictActivityFailure(BaseAuthActivityFailure):
    """Fails the change with the error: no change goes without its record."""

    @t.override
    def _handle(self, error: Exception, record: "AuthActivityRecord") -> None:
        raise error


class AuthSwallowActivityFailure(BaseAuthActivityFailure):
    """Logs the error at ``ERROR`` with the record, and lets the change through."""

    @t.override
    def _handle(self, error: Exception, record: "AuthActivityRecord") -> None:
        logger.error("the activity is not recorded: %r", record, exc_info=error)
