"""
The errors of the operations of the registries; those of their storages are
in :mod:`ingot_auth.storages`.
"""

__all__ = ("AuthItemInvalidError",)

import typing as t

from ingot_auth.storages import AuthRegistryError


class AuthItemInvalidError(AuthRegistryError):
    """
    An id, a name, a type, a source or a value is not acceptable, whatever
    the registry holds.
    """

    @classmethod
    def for_id(cls, registry: str, item_id: int) -> t.Self:
        """The id is not positive."""
        return cls(f"{registry}: the id {item_id} is not positive", registry, item_id)

    @classmethod
    def for_name(cls, registry: str, name: str) -> t.Self:
        """The name does not match the pattern of the names."""
        return cls(f"{registry}: the name {name!r} is not acceptable", registry, name)

    @classmethod
    def for_type(cls, registry: str, item_type: int | str) -> t.Self:
        """The type is not given, or not known."""
        return cls(
            f"{registry}: the type {item_type!r} is not acceptable", registry, item_type
        )

    @classmethod
    def for_value(cls, registry: str, item_id: int) -> t.Self:
        """
        A value of the item ``item_id`` is not acceptable: not of its type, or
        not for the one who gives it. The value itself is not told.
        """
        return cls(
            f"{registry}: a value of {item_id} is not acceptable", registry, item_id
        )

    @classmethod
    def for_source(cls, registry: str, source: int | str) -> t.Self:
        """The source is not given, or not known."""
        return cls(
            f"{registry}: the source {source!r} is not acceptable", registry, source
        )
