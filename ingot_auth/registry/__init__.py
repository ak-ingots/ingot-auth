"""
The registries: what the profiles and the sessions may hold, declared by the
administrator. An item has an explicit id, the same in every environment and
never reused, and a name for people: the tags and the attributes of the
profiles, the attributes of the sessions. The items and their storages are in
:mod:`ingot_auth.storages`; here are the bases of their operations and their
commands.
"""

__all__ = ("AuthItemInvalidError",)

from .errors import AuthItemInvalidError
