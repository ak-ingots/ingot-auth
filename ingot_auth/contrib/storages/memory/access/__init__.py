"""The storage of the access in memory."""

__all__ = ("AuthMemoryAccessStorage", "AuthMemoryMembersStorage")

from ingots.puer import Slot

from ingot_auth.storages import AuthAccessStorage

from .members import AuthMemoryMembersStorage


class AuthMemoryAccessStorage(AuthAccessStorage):
    """The storage of the access in memory."""

    members = Slot(AuthMemoryMembersStorage)
