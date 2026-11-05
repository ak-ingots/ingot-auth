"""The errors of the registries."""

__all__ = (
    "AuthItemConflictError",
    "AuthItemInvalidError",
    "AuthItemNotFoundError",
    "AuthRegistryError",
)

import typing as t


class AuthRegistryError(Exception):
    """
    An error of a registry. ``args`` are the message, the registry and the
    id or the name in question, so the error survives pickling; create it
    with the class methods of its subclasses.
    """

    @property
    def registry(self) -> str:
        """The registry: ``profiles.tags``, ``sessions.attrs``."""
        return t.cast(str, self.args[1])

    @property
    def key(self) -> int | str:
        """The id or the name in question."""
        return t.cast(int | str, self.args[2])

    @t.override
    def __str__(self) -> str:
        return t.cast(str, self.args[0])


class AuthItemConflictError(AuthRegistryError):
    """An id or a name is taken."""

    @classmethod
    def for_id(cls, registry: str, item_id: int) -> t.Self:
        """The id is taken, or was."""
        return cls(f"{registry}: the id {item_id} is not available", registry, item_id)

    @classmethod
    def for_name(cls, registry: str, name: str) -> t.Self:
        """The name is taken."""
        return cls(f"{registry}: the name {name!r} is not available", registry, name)


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


class AuthItemNotFoundError(AuthRegistryError):
    """No item has the id, or an item is not bound to another."""

    @classmethod
    def for_id(cls, registry: str, item_id: int) -> t.Self:
        """No item has ``item_id``."""
        return cls(f"{registry}: no item {item_id}", registry, item_id)

    @classmethod
    def for_binding(cls, registry: str, item_id: int, bound_id: int) -> t.Self:
        """The item ``item_id`` is not bound to ``bound_id``; the key is both."""
        key = f"{item_id}:{bound_id}"
        return cls(f"{registry}: no binding {key}", registry, key)
