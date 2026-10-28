"""The tags: marks on the profiles, declared in a registry."""

__all__ = ("AuthTag", "AuthTags", "BaseAuthTagsStorage")

from ingots.puer import Factory, Slot
from ingots.puer.cli import CliUnit

from .commands import (
    AuthCreateTagCommand,
    AuthDeleteTagCommand,
    AuthListTagsCommand,
    AuthRenameTagCommand,
)
from .items import AuthTag
from .operations import AuthCreateTag, AuthDeleteTag, AuthListTags, AuthRenameTag
from .storage import BaseAuthTagsStorage


class AuthTags(CliUnit):
    """
    The registry of the tags: its operations, ``op_*``, and the commands
    running them, ``cmd_*``; the tags themselves are in the storage of the
    auth.
    """

    cli_name = "tags"
    cli_description = "The tags of the profiles."

    op_create = Factory(AuthCreateTag)
    op_list = Factory(AuthListTags)
    op_rename = Factory(AuthRenameTag)
    op_delete = Factory(AuthDeleteTag)

    cmd_create = Slot(AuthCreateTagCommand)
    cmd_list = Slot(AuthListTagsCommand)
    cmd_rename = Slot(AuthRenameTagCommand)
    cmd_delete = Slot(AuthDeleteTagCommand)
