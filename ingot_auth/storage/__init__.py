"""
The storage of the auth: a facade, a unit a subdomain, the profiles, the
sessions, the sign-up, which a backend in ``ingot_auth.contrib.storages``
implements.
"""

__all__ = ("AuthStorage",)

from ingots.puer import Slot, Unit

from ingot_auth.profile import AuthProfileStorage
from ingot_auth.session import AuthSessionStorage
from ingot_auth.sign_up import AuthSignUpStorage


class AuthStorage(Unit):
    """
    The storage of the auth, every part of it abstract: a backend extends
    it with its own, and the project declares it in the slot of the auth.
    """

    profile = Slot(AuthProfileStorage)
    session = Slot(AuthSessionStorage)
    sign_up = Slot(AuthSignUpStorage)
