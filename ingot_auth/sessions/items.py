"""The caller a session stands for."""

__all__ = ("AuthCaller",)

from dataclasses import dataclass

from ingots.defaults.operations import Caller


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCaller(Caller):
    """
    A caller signed in: the uid of its profile, the permissions the access
    gives it, and the id of its session, which only the operations of the
    sessions read.
    """

    session_id: str
