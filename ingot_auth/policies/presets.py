"""The presets of the policies."""

__all__ = ("AuthPolicyPreset",)

import types
import typing as t

from ingots.puer import Entity

from .errors import AuthPolicyViolationError

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ingot_auth.project import AuthProject

    from .base import AuthPolicyBinding


class AuthPolicyPreset[ContextType](Entity):
    """
    The policies a value of a flow is checked against, the nickname of a
    sign-up, say, in their order, of the context ``ContextType``: a policy is
    bound only if it takes a part the context has. :meth:`_get_bindings` gives
    the bindings by their names, none here: a subclass takes those of its
    base and adds, replaces or drops some::

        @t.override
        def _get_bindings(self) -> dict[str, AuthPolicyBinding[Context, t.Any]]:
            bindings = super()._get_bindings()
            bindings["length"] = AuthLengthPolicy.bind(AuthLengthConfig(min=5))
            return bindings

    A preset is a slot ``preset_<flow>_<field>`` of the method it checks a
    field of, its class a subclass of that of the slot it replaces.
    """

    project: "AuthProject"

    @t.final
    def get_bindings(self) -> "Mapping[str, AuthPolicyBinding[ContextType, t.Any]]":
        """The bindings by their names, in the order they are checked."""
        return types.MappingProxyType(self._get_bindings())

    @t.final
    async def check(self, context: ContextType) -> None:
        """
        Checks a context against the policies bound, the first broken raising.

        :raises AuthPolicyViolationError: the context breaks one.
        :raises AuthPolicyNotFoundError: no slot holds the policy of a binding.
        """
        policies = self.project.auth.policies
        for name, binding in self._get_bindings().items():
            policy = policies.find(binding.policy)
            if not await policy.accepts(context, binding.config):
                raise AuthPolicyViolationError.for_binding(name)

    def _get_bindings(self) -> "dict[str, AuthPolicyBinding[ContextType, t.Any]]":
        """The bindings by their names, a new dict on every call."""
        return {}
