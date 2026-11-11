"""What the storage of the sign-up keeps: the record of a sign-up."""

__all__ = ("AuthSignUpRecord",)

import datetime
import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ..items import AuthAttrValue


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSignUpRecord:
    """
    What a sign-up happened on: the profile, the method, the time and the
    values of the attributes of the session, for the analytics among others.
    Not a session: a sign-up opens none.
    """

    uid: str
    method: str
    signed_up_at: datetime.datetime
    values: "Mapping[int, AuthAttrValue]"
