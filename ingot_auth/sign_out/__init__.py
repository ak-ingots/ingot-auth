"""
The sign-out: the caller closes its session, its token working no more from
the very next request. Open to any caller: one of no session, the anonymous
one of a token closed, expired or unknown, signs out of nothing, so that a
client may retry and an attacker learns nothing.
"""

__all__ = ("AuthSignOutOperation", "AuthSignOutUnit")

from ingots.puer import Factory, Unit

from .operations import AuthSignOutOperation


class AuthSignOutUnit(Unit):
    """
    The sign-out, a unit of its own as the sign-in is: its operation requires
    no permission, so that the unit binds none.
    """

    op_sign_out = Factory(AuthSignOutOperation)
