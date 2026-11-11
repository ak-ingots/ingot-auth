"""The storage of the sign-up in memory."""

__all__ = ("AuthMemorySignUpRecordsStorage", "AuthMemorySignUpStorage")

from ingots.puer import Slot

from ingot_auth.storages import AuthSignUpStorage

from .records import AuthMemorySignUpRecordsStorage


class AuthMemorySignUpStorage(AuthSignUpStorage):
    """The storage of the sign-up in memory."""

    records = Slot(AuthMemorySignUpRecordsStorage)
