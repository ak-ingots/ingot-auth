"""The operations of a registry, a subclass for each: tags, attributes."""

__all__ = (
    "AuthDeleteItemParameters",
    "AuthRenameItemParameters",
    "BaseAuthCreateItemOperation",
    "BaseAuthDeleteItemOperation",
    "BaseAuthListItemsOperation",
    "BaseAuthRegistryOperation",
    "BaseAuthRenameItemOperation",
)

import abc
import re
import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata
from ingots.puer import Unit

from ingot_auth.activities import AuthActivityContext
from ingot_auth.storages import AuthActivityAction, AuthItem, BaseAuthRegistryStorage

from .errors import AuthItemInvalidError

if t.TYPE_CHECKING:
    from ingot_auth.project import AuthProject


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRenameItemParameters:
    uid: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthItemRenamed(AuthActivityContext):
    """The context of an item renamed in the activity log: its new name."""

    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthDeleteItemParameters:
    uid: int


class BaseAuthRegistryOperation[ItemType: AuthItem, ParametersType, ResultType](
    BaseOperation[ParametersType, ResultType]
):
    """
    An operation of a registry: a subclass gives the storage of its own,
    ``self.project.auth.storage.profiles.tags`` for instance. Names are a word or
    words joined by ``/`` (``title/en``), in lower case: another
    :attr:`NAME_PATTERN` changes that.
    """

    NAME_PATTERN: t.ClassVar[re.Pattern[str]] = re.compile(
        r"[a-z][a-z0-9_]*(/[a-z0-9_]+)*"
    )

    project: "AuthProject"

    @abc.abstractmethod
    def _get_storage(self) -> BaseAuthRegistryStorage[ItemType]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_storage")

    def _check_name(self, name: str) -> None:
        if not self.NAME_PATTERN.fullmatch(name):
            raise AuthItemInvalidError.for_name(self._get_storage().REGISTRY, name)

    @t.final
    async def _record(
        self,
        item_uid: int,
        action: AuthActivityAction,
        metadata: OperationMetadata,
        context: AuthActivityContext | None = None,
    ) -> None:
        """Records the change of an item in the activity log, the registry its type."""
        await self.project.auth.activities.record(
            self.find_parent(Unit), str(item_uid), action, metadata, context=context
        )


class BaseAuthCreateItemOperation[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, ItemType, ItemType]
):
    """
    Creates an item, returning it, recorded in the activity log with the context
    of :meth:`_get_created_context`, none by default.
    """

    @t.override
    async def _run(self, parameters: ItemType, metadata: OperationMetadata) -> ItemType:
        storage = self._get_storage()
        if parameters.uid < 1:
            raise AuthItemInvalidError.for_uid(storage.REGISTRY, parameters.uid)
        self._check_name(parameters.name)
        async with self.project.auth.storage.transaction():
            await storage.create(parameters)
            await self._record(
                parameters.uid,
                AuthActivityAction.CREATE,
                metadata,
                self._get_created_context(parameters),
            )
        return parameters

    def _get_created_context(self, item: ItemType) -> AuthActivityContext | None:
        """What the log keeps of an item created: nothing, as of a tag."""
        return None


class BaseAuthListItemsOperation[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, None, tuple[ItemType, ...]]
):
    """The items, by id."""

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[ItemType, ...]:
        return await self._get_storage().get_all()


class BaseAuthRenameItemOperation[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, AuthRenameItemParameters, ItemType]
):
    """Gives an item a new name, returning the item renamed, recorded with it."""

    @t.override
    async def _run(
        self, parameters: AuthRenameItemParameters, metadata: OperationMetadata
    ) -> ItemType:
        self._check_name(parameters.name)
        async with self.project.auth.storage.transaction():
            renamed = await self._get_storage().rename(parameters.uid, parameters.name)
            await self._record(
                parameters.uid,
                AuthActivityAction.UPDATE,
                metadata,
                AuthItemRenamed(name=parameters.name),
            )
        return renamed


class BaseAuthDeleteItemOperation[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, AuthDeleteItemParameters, None]
):
    """
    Deletes an item, recorded in the activity log; its id is never given
    again. What refers to it, the profiles, is not looked at yet.
    """

    @t.override
    async def _run(
        self, parameters: AuthDeleteItemParameters, metadata: OperationMetadata
    ) -> None:
        async with self.project.auth.storage.transaction():
            await self._get_storage().delete(parameters.uid)
            await self._record(parameters.uid, AuthActivityAction.DELETE, metadata)
