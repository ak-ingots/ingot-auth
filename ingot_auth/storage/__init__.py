"""
The storage of the auth: a facade, a unit for the profiles and one for the
sessions, one storage a registry, which a backend in
``ingot_auth.contrib.storages`` implements.
"""

__all__ = ("AuthStorage",)

from ingots.puer import Slot, Unit

from ingot_auth.profile import AuthProfileStorage
from ingot_auth.session import AuthSessionStorage


class AuthStorage(Unit):
    """
    The storage of the auth, every part of it abstract: a backend extends
    it with its own, and the project declares it in the slot of the auth.
    """

    profile = Slot(AuthProfileStorage)
    session = Slot(AuthSessionStorage)
