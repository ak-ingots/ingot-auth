"""
The policies: the rules a value is checked against, each an entity of the
project in the registry :class:`AuthPoliciesUnit`, found by its class, and their
presets, the policies a field of a flow is checked against, bound with their
configs. A policy takes the part of a context its protocol tells, and a
preset is bound only the policies its context has the parts of. The core
gives the policies needing nothing more, the length and the characters; a
preset is of the method whose field it checks, a slot of the method. An
application adds its policies as slots of :class:`AuthPoliciesUnit`::

    class AppPolicies(AuthPoliciesUnit):
        banned_words = Slot(AppBannedWordsPolicy)
"""

__all__ = (
    "AuthChars",
    "AuthCharsConfig",
    "AuthCharsPolicy",
    "AuthHasValue",
    "AuthLengthConfig",
    "AuthLengthPolicy",
    "AuthPoliciesUnit",
    "AuthPolicyBinding",
    "AuthPolicyNotFoundError",
    "AuthPolicyPreset",
    "AuthPolicyViolationError",
    "AuthValueContext",
    "BaseAuthPolicy",
)

import typing as t

from ingots.puer import Slot, Unit

from .base import AuthPolicyBinding, BaseAuthPolicy
from .chars import AuthChars, AuthCharsConfig, AuthCharsPolicy
from .contexts import AuthHasValue, AuthValueContext
from .errors import AuthPolicyNotFoundError, AuthPolicyViolationError
from .length import AuthLengthConfig, AuthLengthPolicy
from .presets import AuthPolicyPreset


class AuthPoliciesUnit(Unit):
    """The registry of the policies of the project, one a class, found by it."""

    length = Slot(AuthLengthPolicy)
    chars = Slot(AuthCharsPolicy)

    @t.final
    def find[PolicyType: BaseAuthPolicy[t.Any, t.Any]](
        self, kind: type[PolicyType]
    ) -> PolicyType:
        """
        The policy of a class: of the first slot holding it or a subclass.

        :raises AuthPolicyNotFoundError: no slot holds one.
        """
        for name, _ in type(self).slots_iter(kind):
            return self.slots_find_entity(name, kind)
        raise AuthPolicyNotFoundError.for_kind(kind)
