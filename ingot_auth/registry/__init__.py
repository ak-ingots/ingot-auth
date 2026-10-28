"""
The registries: what the profiles may hold, declared by the administrator.
An item has an explicit id, the same in every environment and never reused,
and a name for people. The tags and the attributes are registries; the
attributes of the sessions will be one.
"""

__all__ = (
    "AuthItem",
    "AuthItemConflictError",
    "AuthItemNotFoundError",
    "AuthMemoryRegistryStorage",
    "AuthRegistryError",
    "BaseAuthRegistryStorage",
)

from .errors import AuthItemConflictError, AuthItemNotFoundError, AuthRegistryError
from .items import AuthItem
from .storage import AuthMemoryRegistryStorage, BaseAuthRegistryStorage
