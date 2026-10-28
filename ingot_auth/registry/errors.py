"""The errors of the registries."""

__all__ = ("AuthItemConflictError", "AuthItemNotFoundError", "AuthRegistryError")

import typing as t


class AuthRegistryError(Exception):
    """
    An error of a registry. ``args`` are the message, the registry and the
    id or the name in question, so the error survives pickling; create it
    with the class methods of its subclasses.
    """

    @property
    def registry(self) -> str:
        """The registry: ``tags``, ``attrs``."""
        return t.cast(str, self.args[1])

    @property
    def key(self) -> int | str:
        """The id or the name in question."""
        return t.cast(int | str, self.args[2])

    @t.override
    def __str__(self) -> str:
        return t.cast(str, self.args[0])


class AuthItemConflictError(AuthRegistryError):
    """An id or a name is taken, or not acceptable."""

    @classmethod
    def for_id(cls, registry: str, item_id: int) -> t.Self:
        """The id is taken, or was, or is not positive."""
        return cls(f"{registry}: the id {item_id} is not available", registry, item_id)

    @classmethod
    def for_name(cls, registry: str, name: str) -> t.Self:
        """The name is taken, or not acceptable."""
        return cls(f"{registry}: the name {name!r} is not available", registry, name)


class AuthItemNotFoundError(AuthRegistryError):
    """No item has the id."""

    @classmethod
    def for_id(cls, registry: str, item_id: int) -> t.Self:
        """No item has ``item_id``."""
        return cls(f"{registry}: no item {item_id}", registry, item_id)
