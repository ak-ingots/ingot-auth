"""The base of the policies, and their bindings."""

__all__ = ("AuthPolicyBinding", "BaseAuthPolicy")

import abc
import typing as t
from dataclasses import dataclass

from ingots.puer import Entity

# declared, as mypy infers no variance through the class of a policy: a
# binding of a policy of a part of a context is one of a context with it
ContextT_contra = t.TypeVar("ContextT_contra", contravariant=True)
ConfigT_co = t.TypeVar("ConfigT_co", covariant=True)


@dataclass(frozen=True, slots=True)
class AuthPolicyBinding(t.Generic[ContextT_contra, ConfigT_co]):
    """
    A policy bound to a preset with the config it is checked by: made by the
    policy, :meth:`BaseAuthPolicy.bind`, so that its config is of the type
    the policy takes and the context of the preset has the part it takes.
    """

    policy: "type[BaseAuthPolicy[t.Any, t.Any]]"
    config: ConfigT_co


class BaseAuthPolicy[ContextType, ConfigType](Entity):
    """
    A rule a value is checked against, a nickname, a password: one entity of
    the project, configured anew by every binding that takes it, so that a
    policy of a list or a dictionary loads it once. It takes the part of a
    context its protocol tells, ``ContextType``; the config is data, given to
    a client as well, to check a form before sending it.

    A policy is a slot of :class:`AuthPolicies`, found by its class.
    """

    @t.final
    @classmethod
    def bind(cls, config: ConfigType) -> AuthPolicyBinding[ContextType, ConfigType]:
        """The policy with a config, for a preset of a context it takes."""
        return AuthPolicyBinding(cls, config)

    @t.final
    async def accepts(self, context: ContextType, config: ConfigType) -> bool:
        """Whether the context keeps the policy, as the config tells it."""
        return await self._accepts(context, config)

    @abc.abstractmethod
    async def _accepts(self, context: ContextType, config: ConfigType) -> bool:
        raise NotImplementedError(f"{type(self).__qualname__}._accepts")
