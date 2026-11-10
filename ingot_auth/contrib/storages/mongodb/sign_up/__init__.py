"""The storage of the sign-up in MongoDB."""

__all__ = ("AuthMongoDbSignUpRecordsStorage", "AuthMongoDbSignUpStorage")

from ingots.puer import Slot

from ingot_auth.sign_up import AuthSignUpStorage

from .records import AuthMongoDbSignUpRecordsStorage


class AuthMongoDbSignUpStorage(AuthSignUpStorage):
    """The storage of the sign-up in MongoDB."""

    records = Slot(AuthMongoDbSignUpRecordsStorage)
