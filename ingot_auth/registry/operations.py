"""The operations of a registry, a subclass for each: tags, attributes."""

__all__ = (
    "AuthDeleteItemParameters",
    "AuthRenameItemParameters",
    "BaseAuthCreateItem",
    "BaseAuthDeleteItem",
    "BaseAuthListItems",
    "BaseAuthRegistryOperation",
    "BaseAuthRenameItem",
)

import abc
import re
import typing as t
from dataclasses import dataclass

from ingots.defaults.operations import BaseOperation, OperationMetadata

from .errors import AuthItemConflictError
from .items import AuthItem
from .storage import BaseAuthRegistryStorage


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthRenameItemParameters:
    id: int
    name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthDeleteItemParameters:
    id: int


class BaseAuthRegistryOperation[ItemType: AuthItem, ParametersType, ResultType](
    BaseOperation[ParametersType, ResultType]
):
    """
    An operation of a registry: a subclass gives the storage of its own,
    ``self.project.auth.storage.tags`` for instance. Names are a word or
    words joined by ``/`` (``title/en``), in lower case: another
    :attr:`NAME_PATTERN` changes that.
    """

    NAME_PATTERN: t.ClassVar[re.Pattern[str]] = re.compile(
        r"[a-z][a-z0-9_]*(/[a-z0-9_]+)*"
    )

    @abc.abstractmethod
    def _get_storage(self) -> BaseAuthRegistryStorage[ItemType]:
        raise NotImplementedError(f"{type(self).__qualname__}._get_storage")

    def _check_name(self, name: str) -> None:
        if not self.NAME_PATTERN.fullmatch(name):
            raise AuthItemConflictError.for_name(self._get_storage().REGISTRY, name)


class BaseAuthCreateItem[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, ItemType, ItemType]
):
    """Creates an item, returning it."""

    @t.override
    async def _run(self, parameters: ItemType, metadata: OperationMetadata) -> ItemType:
        storage = self._get_storage()
        if parameters.id < 1:
            raise AuthItemConflictError.for_id(storage.REGISTRY, parameters.id)
        self._check_name(parameters.name)
        await storage.create(parameters)
        return parameters


class BaseAuthListItems[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, None, tuple[ItemType, ...]]
):
    """The items, by id."""

    @t.override
    async def _run(
        self, parameters: None, metadata: OperationMetadata
    ) -> tuple[ItemType, ...]:
        return await self._get_storage().get_all()


class BaseAuthRenameItem[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, AuthRenameItemParameters, ItemType]
):
    """Gives an item a new name, returning the item renamed."""

    @t.override
    async def _run(
        self, parameters: AuthRenameItemParameters, metadata: OperationMetadata
    ) -> ItemType:
        self._check_name(parameters.name)
        return await self._get_storage().rename(parameters.id, parameters.name)


class BaseAuthDeleteItem[ItemType: AuthItem](
    BaseAuthRegistryOperation[ItemType, AuthDeleteItemParameters, None]
):
    """
    Deletes an item; its id is never given again. What refers to it, the
    profiles, is not looked at yet.
    """

    @t.override
    async def _run(
        self, parameters: AuthDeleteItemParameters, metadata: OperationMetadata
    ) -> None:
        await self._get_storage().delete(parameters.id)
