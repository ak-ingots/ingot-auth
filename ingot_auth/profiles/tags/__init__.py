"""The tags: marks on the profiles, declared in a registry."""

__all__ = (
    "AuthTagsUnit",
    "AuthTagsPermissions",
)

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateTagCommand,
    AuthDeleteTagCommand,
    AuthListTagsCommand,
    AuthRenameTagCommand,
)
from .operations import (
    AuthCreateTagOperation,
    AuthDeleteTagOperation,
    AuthListTagsOperation,
    AuthRenameTagOperation,
)
from .permissions import AuthTagsPermissions


class AuthTagsUnit(CliUnit):
    """
    The registry of the tags: its operations, ``op_*``, and the commands
    running them, ``cmd_*``; the tags themselves are in the storage of the
    auth.
    """

    cli_name = "tags"
    cli_description = "The tags of the profiles."

    op_create = Factory(AuthCreateTagOperation)
    op_list = Factory(AuthListTagsOperation)
    op_rename = Factory(AuthRenameTagOperation)
    op_delete = Factory(AuthDeleteTagOperation)

    cmd_create = Slot(AuthCreateTagCommand)
    cmd_list = Slot(AuthListTagsCommand)
    cmd_rename = Slot(AuthRenameTagCommand)
    cmd_delete = Slot(AuthDeleteTagCommand)
