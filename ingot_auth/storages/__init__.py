"""
The storages of the auth: the interfaces a backend in
``ingot_auth.contrib.storages`` implements, with what they keep and what they
raise, depending on no other part of the auth. :class:`AuthStorage` is the
facade, a unit a subdomain, the profiles, the sessions, the sign-up, the
access, and the activity log, with the transactions of the backend over all
of them.
"""

__all__ = (
    "ATTR_VALUE_TYPES",
    "AuthAccessStorage",
    "AuthActivityAction",
    "AuthActivityQuery",
    "AuthActivityRecord",
    "AuthAttr",
    "AuthAttrType",
    "AuthAttrValue",
    "AuthIdentity",
    "AuthIdentityConflictError",
    "AuthIdentityError",
    "AuthIdentityNotFoundError",
    "AuthItem",
    "AuthItemConflictError",
    "AuthItemNotFoundError",
    "AuthMembership",
    "AuthProfile",
    "AuthProfileConflictError",
    "AuthProfileError",
    "AuthProfileNotFoundError",
    "AuthProfileValues",
    "AuthProfilesStorage",
    "AuthRegistryError",
    "AuthSecretNotFoundError",
    "AuthSessionAttr",
    "AuthSessionAttrSource",
    "AuthSessionCloseReason",
    "AuthSessionError",
    "AuthSessionNotFoundError",
    "AuthSessionPreset",
    "AuthSessionPresetBinding",
    "AuthSessionRecord",
    "AuthSessionsStorage",
    "AuthSignUpRecord",
    "AuthSignUpRecordNotFoundError",
    "AuthSignUpStorage",
    "AuthStorage",
    "AuthTag",
    "AuthTransactionError",
    "BaseAuthActivitiesStorage",
    "BaseAuthAttrsStorage",
    "BaseAuthIdentitiesStorage",
    "BaseAuthMembersStorage",
    "BaseAuthRegistryStorage",
    "BaseAuthProfileValuesStorage",
    "BaseAuthSecretsStorage",
    "BaseAuthSessionAttrsStorage",
    "BaseAuthSessionPresetsStorage",
    "BaseAuthSignUpRecordsStorage",
    "BaseAuthTagsStorage",
)

import abc
import contextlib
import contextvars
import types
import typing as t

from ingots.puer import Slot, Unit

from .access import AuthAccessStorage, AuthMembership, BaseAuthMembersStorage
from .errors import (
    AuthItemConflictError,
    AuthItemNotFoundError,
    AuthRegistryError,
    AuthTransactionError,
)
from .activities import (
    AuthActivityAction,
    AuthActivityQuery,
    AuthActivityRecord,
    BaseAuthActivitiesStorage,
)
from .data import ATTR_VALUE_TYPES, AuthAttrType, AuthAttrValue, AuthItem
from .profiles import (
    AuthAttr,
    AuthIdentity,
    AuthIdentityConflictError,
    AuthIdentityError,
    AuthIdentityNotFoundError,
    AuthProfile,
    AuthProfileConflictError,
    AuthProfileError,
    AuthProfileNotFoundError,
    AuthProfilesStorage,
    AuthProfileValues,
    AuthSecretNotFoundError,
    AuthTag,
    BaseAuthAttrsStorage,
    BaseAuthIdentitiesStorage,
    BaseAuthProfileValuesStorage,
    BaseAuthSecretsStorage,
    BaseAuthTagsStorage,
)
from .registry import BaseAuthRegistryStorage
from .sessions import (
    AuthSessionAttr,
    AuthSessionAttrSource,
    AuthSessionCloseReason,
    AuthSessionError,
    AuthSessionNotFoundError,
    AuthSessionPreset,
    AuthSessionPresetBinding,
    AuthSessionRecord,
    AuthSessionsStorage,
    BaseAuthSessionAttrsStorage,
    BaseAuthSessionPresetsStorage,
)
from .sign_up import (
    AuthSignUpRecord,
    AuthSignUpRecordNotFoundError,
    AuthSignUpStorage,
    BaseAuthSignUpRecordsStorage,
)

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping

    from ingots.defaults import Project


# the transactions of the current context, by their storages: one variable
# of the module, as the context keeps its variables for good; a new mapping
# on every change, so a task does not see what another sets
_transactions: "contextvars.ContextVar[Mapping[AuthStorage, object]]" = (
    contextvars.ContextVar(
        "ingot_auth.storages.transactions", default=types.MappingProxyType({})
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

    # the project of the defaults of ingots: its events, which a transaction
    # holds; the storage depends on no other part of the auth
    project: "Project"

    # mypy refuses an abstract class where a type is expected: a slot of
    # one is an open question of ingots
    profiles = Slot(AuthProfilesStorage)  # type: ignore[type-abstract]
    sessions = Slot(AuthSessionsStorage)  # type: ignore[type-abstract]
    sign_up = Slot(AuthSignUpStorage)
    access = Slot(AuthAccessStorage)
    activities = Slot(BaseAuthActivitiesStorage)  # type: ignore[type-abstract]

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
        back when it raises. Inside another, it is that one. It holds the
        events published in its block, ``project.events`` of ingots: they go
        once it commits, when the outermost hold ends, and are dropped when
        it rolls back or fails to commit.
        """
        if self.get_transaction() is not None:
            yield
            return
        async with self.project.events.hold() as held:
            await self.begin()
            try:
                yield
            except BaseException:
                held.discard()
                await self.rollback()
                raise
            try:
                await self.commit()
            except BaseException:
                held.discard()
                raise

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
