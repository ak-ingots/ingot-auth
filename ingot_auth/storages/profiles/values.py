"""
The storage of the values of the profiles: the tags a profile has and the
values of its attributes, by the ids of their registries, apart from the
profile itself, which holds its uid and its time alone.
"""

__all__ = ("BaseAuthProfileValuesStorage",)

import abc
import typing as t

from ingots.puer import Entity

from .data import AuthProfileValues

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ..data import AuthAttrValue


class BaseAuthProfileValuesStorage(Entity):
    """
    The storage of the values of the profiles: what a backend implements.
    Each set replaces the whole set, the tags or the values, a profile of
    none having empty ones; whether the profile, the tags and the attributes
    are, the operations check.
    """

    @t.final
    async def get(self, uid: str) -> AuthProfileValues:
        """The values of a profile, empty for one of none."""
        return await self._get(uid)

    @t.final
    async def set_tags(self, uid: str, tag_uids: frozenset[int]) -> None:
        """Keeps the tags of a profile, in place of those it had."""
        await self._set_tags(uid, tag_uids)

    @t.final
    async def set_attr_values(
        self, uid: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> None:
        """Keeps the values of the attributes of a profile, in place of those."""
        await self._set_attr_values(uid, attr_values)

    @abc.abstractmethod
    async def _get(self, uid: str) -> AuthProfileValues:
        raise NotImplementedError(f"{type(self).__qualname__}._get")

    @abc.abstractmethod
    async def _set_tags(self, uid: str, tag_uids: frozenset[int]) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._set_tags")

    @abc.abstractmethod
    async def _set_attr_values(
        self, uid: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> None:
        raise NotImplementedError(f"{type(self).__qualname__}._set_attr_values")
