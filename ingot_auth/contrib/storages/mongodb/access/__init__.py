"""The storage of the access in MongoDB."""

__all__ = ("AuthMongoDbAccessStorage", "AuthMongoDbMembersStorage")

from ingots.puer import Slot

from ingot_auth.access import AuthAccessStorage

from .members import AuthMongoDbMembersStorage


class AuthMongoDbAccessStorage(AuthAccessStorage):
    """The storage of the access in MongoDB."""

    members = Slot(AuthMongoDbMembersStorage)
