"""
The storage of the auth: a facade, a unit a subdomain, the profiles, the
sessions, the sign-up, the access, which a backend in ``ingot_auth.contrib.storages``
implements, with the transactions of the backend over all of them.
"""

__all__ = ("AuthStorage", "AuthTransactionError")

import abc
import contextlib
import contextvars
import types
import typing as t

from ingots.puer import Slot, Unit

from ingot_auth.access import AuthAccessStorage
from ingot_auth.profiles import AuthProfilesStorage
from ingot_auth.sessions import AuthSessionsStorage
from ingot_auth.sign_up import AuthSignUpStorage

from .errors import AuthTransactionError

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping


# the transactions of the current context, by their storages: one variable
# of the module, as the context keeps its variables for good; a new mapping
# on every change, so a task does not see what another sets
_transactions: "contextvars.ContextVar[Mapping[AuthStorage, object]]" = (
    contextvars.ContextVar(
        "ingot_auth.storage.transactions", default=types.MappingProxyType({})
    )
)


class AuthStorage(Unit):
    """
    The storage of the auth, every part of it abstract: a backend extends
    it with its own, and the project declares it in the slot of the auth.

    A transaction of the backend spans its storages: what is written in it
    is kept by :meth:`commit` and undone by :meth:`rollback`, all of it.
    :meth:`transaction` is the usual way; the methods are there for who
    begins in one place and ends in another. The transaction is of the
    current context, so of a task of asyncio: the storages of the backend
    reach it with :meth:`get_transaction`.
    """

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    profiles = Slot(AuthProfilesStorage)  # type: ignore[type-abstract]
    sessions = Slot(AuthSessionsStorage)
    sign_up = Slot(AuthSignUpStorage)
    access = Slot(AuthAccessStorage)

    @t.final
    def get_transaction(self) -> object | None:
        """
        What the backend keeps of the transaction of the current context, a
        session of its client, say; ``None`` outside one.
        """
        return _transactions.get().get(self)

    @t.final
    async def begin(self) -> None:
        """
        Begins a transaction in the current context.

        :raises AuthTransactionError: one is begun already.
        """
        if self.get_transaction() is not None:
            raise AuthTransactionError.for_begun()
        transaction = await self._begin()
        _transactions.set({**_transactions.get(), self: transaction})

    @t.final
    async def commit(self) -> None:
        """
        Keeps what the transaction of the current context wrote, and ends it.

        :raises AuthTransactionError: none is begun.
        """
        transaction = self._end()
        await self._commit(transaction)

    @t.final
    async def rollback(self) -> None:
        """
        Undoes what the transaction of the current context wrote, and ends it.

        :raises AuthTransactionError: none is begun.
        """
        transaction = self._end()
        await self._rollback(transaction)

    @t.final
    @contextlib.asynccontextmanager
    async def transaction(self) -> "AsyncIterator[None]":
        """
        A transaction around a block: committed when the block ends, rolled
        back when it raises. Inside another, it is that one.
        """
        if self.get_transaction() is not None:
            yield
            return
        await self.begin()
        try:
            yield
        except BaseException:
            await self.rollback()
            raise
        await self.commit()

    @abc.abstractmethod
    async def _begin(self) -> object:
        """Begins a transaction of the backend: what it keeps of it."""
        raise NotImplementedError(f"{type(self).__qualname__}._begin")

    @abc.abstractmethod
    async def _commit(self, transaction: object) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._commit")

    @abc.abstractmethod
    async def _rollback(self, transaction: object) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._rollback")

    def _end(self) -> object:
        transactions = dict(_transactions.get())
        transaction = transactions.pop(self, None)
        if transaction is None:
            raise AuthTransactionError.for_not_begun()
        _transactions.set(transactions)
        return transaction
