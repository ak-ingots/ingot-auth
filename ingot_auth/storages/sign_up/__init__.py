"""The storage of the sign-up: its records."""

__all__ = (
    "AuthSignUpRecord",
    "AuthSignUpRecordNotFoundError",
    "AuthSignUpStorage",
    "BaseAuthSignUpRecordsStorage",
)

from ingots.puer import Slot, Unit

from .errors import AuthSignUpRecordNotFoundError
from .data import AuthSignUpRecord
from .records import BaseAuthSignUpRecordsStorage


class AuthSignUpStorage(Unit):
    """The storage of the sign-up, every part of it abstract."""

    records = Slot(BaseAuthSignUpRecordsStorage)  # type: ignore[type-abstract]
