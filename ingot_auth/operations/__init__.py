"""The operations unit of the defaults with the callers of the addon."""

__all__ = ("AuthCallersProvider", "AuthOperationsUnit")

from ingots.defaults.operations import OperationsUnit
from ingots.puer import Slot

from .callers import AuthCallersProvider


class AuthOperationsUnit(OperationsUnit):
    """The operations unit, with the addon's :class:`AuthCallersProvider`."""

    callers = Slot(AuthCallersProvider)
