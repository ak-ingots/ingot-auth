"""
The registries: what the profiles and the sessions may hold, declared by the
administrator. An item has an explicit id, the same in every environment and
never reused, and a name for people: the tags and the attributes of the
profiles, the attributes of the sessions.
"""

__all__ = (
    "ATTR_VALUE_TYPES",
    "AuthAttrType",
    "AuthAttrValue",
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
from .items import ATTR_VALUE_TYPES, AuthAttrType, AuthAttrValue, AuthItem
from .storage import BaseAuthRegistryStorage
