"""
The registries: what the profiles and the sessions may hold, declared by the
administrator. An item has an explicit id, the same in every environment and
never reused, and a name for people: the tags and the attributes of the
profiles, the attributes of the sessions.
"""

__all__ = (
    "AuthAttrType",
    "AuthItem",
    "AuthItemConflictError",
    "AuthItemInvalidError",
    "AuthItemNotFoundError",
    "AuthRegistryError",
    "BaseAuthRegistryStorage",
)

from .errors import (
    AuthItemConflictError,
    AuthItemInvalidError,
    AuthItemNotFoundError,
    AuthRegistryError,
)
from .items import AuthAttrType, AuthItem
from .storage import BaseAuthRegistryStorage
