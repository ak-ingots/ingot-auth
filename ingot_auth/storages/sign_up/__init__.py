"""The storage of the sign-up: its records."""

__all__ = (
    "AuthSignUpRecord",
    "AuthSignUpRecordNotFoundError",
    "AuthSignUpStorage",
    "BaseAuthSignUpRecordsStorage",
)

from ingots.puer import Slot, Unit

from .errors import AuthSignUpRecordNotFoundError
from .items import AuthSignUpRecord
from .records import BaseAuthSignUpRecordsStorage


class AuthSignUpStorage(Unit):
    """The storage of the sign-up, every part of it abstract."""

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    records = Slot(BaseAuthSignUpRecordsStorage)  # type: ignore[type-abstract]
