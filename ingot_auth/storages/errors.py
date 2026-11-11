"""The errors of the storages: of the transactions, and of the registries."""

__all__ = (
    "AuthItemConflictError",
    "AuthItemNotFoundError",
    "AuthRegistryError",
    "AuthTransactionError",
)

import typing as t


class AuthTransactionError(Exception):
    """
    A transaction is begun, committed or rolled back out of turn: a call of
    the storage is wrong, not the data. ``args`` are the message.
    """

    @classmethod
    def for_begun(cls) -> t.Self:
        return cls("a transaction is begun already")

    @classmethod
    def for_not_begun(cls) -> t.Self:
        return cls("no transaction is begun")

    @t.override
    def __str__(self) -> str:
        return str(self.args[0])


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
