"""The strategies deriving the values of attributes of a session."""

__all__ = ("AuthNoSessionAttrsDeriver", "BaseAuthSessionAttrsDeriver")

import abc
import typing as t

from ingots.puer import Entity

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.storages import AuthAttrValue


class BaseAuthSessionAttrsDeriver(Entity):
    """
    The strategy deriving the values of the attributes of a session of the
    source ``derived`` from those the client and the transport gave at the
    start of its flow, by the names of their attributes, the place from the
    IP: in the slot ``deriver`` of the sessions, which the application
    declares, as the sessions have none. The registry keeps those it has of
    the source and of their types, as it keeps those of the transport.
    """

    @t.final
    async def derive(
        self, attr_values: "Mapping[str, AuthAttrValue]"
    ) -> "Mapping[str, AuthAttrValue]":
        """The values derived from those given, by the names of their attributes."""
        return await self._derive(attr_values)

    @abc.abstractmethod
    async def _derive(
        self, attr_values: "Mapping[str, AuthAttrValue]"
    ) -> "Mapping[str, AuthAttrValue]":
        raise NotImplementedError(f"{type(self).__qualname__}._derive")


class AuthNoSessionAttrsDeriver(BaseAuthSessionAttrsDeriver):
    """Derives none: the pick of an application that tells no place."""

    @t.override
    async def _derive(
        self, attr_values: "Mapping[str, AuthAttrValue]"
    ) -> "Mapping[str, AuthAttrValue]":
        return {}
