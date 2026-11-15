"""The values of the profiles in memory."""

__all__ = ("AuthMemoryProfileValuesStorage",)

import dataclasses
import typing as t

from ingot_auth.storages import AuthProfileValues, BaseAuthProfileValuesStorage

from ..state import AuthMemoryStateMixin

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


class AuthMemoryProfileValuesStorage(
    AuthMemoryStateMixin, BaseAuthProfileValuesStorage
):
    """The values of the profiles in memory, by the uids of their profiles."""

    def __init__(self) -> None:
        super().__init__()
        self._values: dict[str, AuthProfileValues] = {}

    @t.override
    async def _get(self, uid: str) -> AuthProfileValues:
        return self._values.get(uid, AuthProfileValues())

    @t.override
    async def _set_tags(self, uid: str, tag_ids: frozenset[int]) -> None:
        values = await self._get(uid)
        self._values[uid] = dataclasses.replace(values, tag_ids=tag_ids)

    @t.override
    async def _set_attr_values(
        self, uid: str, attr_values: "Mapping[int, AuthAttrValue]"
    ) -> None:
        values = await self._get(uid)
        self._values[uid] = dataclasses.replace(values, attr_values=dict(attr_values))
