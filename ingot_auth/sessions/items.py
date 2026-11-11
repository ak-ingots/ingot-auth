"""What opening a session gives."""

__all__ = ("AuthSessionToken",)

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthSessionToken:
    """
    The token of a session just opened, given once, kept by none but the
    client and never in a ``repr``, and the id of its session, public.
    """

    session_id: str
    token: str = field(repr=False)
