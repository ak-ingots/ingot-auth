"""The values of the attributes of the profiles, on the command line."""

__all__ = ("AuthProfileAttrValuesUnit", "AuthSetProfileAttrValuesCommand")

from ingots.puer import Slot
from ingots.puer.cli import CliUnit

from .commands import AuthSetProfileAttrValuesCommand


class AuthProfileAttrValuesUnit(CliUnit):
    """
    The values of the attributes of the profiles, set by an operator:
    ``auth profiles attrs values set``. The operation is of the profiles,
    ``auth.profiles.op_set_attr_values``, the registry of the attributes
    above it.
    """

    cli_name = "values"
    cli_description = "The values of the attributes of the profiles."

    cmd_set = Slot(AuthSetProfileAttrValuesCommand)
