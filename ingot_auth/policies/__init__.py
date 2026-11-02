"""
The policies: the rules a value is checked against, each an entity of the
project, found by its class, and their presets, the policies a value of a
flow is checked against, bound with their configs. A policy takes the part of
a context its protocol tells, and a preset is bound only the policies its
context has the parts of. The core gives the policies needing nothing more,
the length and the characters, and the presets of the values of the flows,
empty: the code of a flow reaches its preset as an attribute, so that mypy
checks the context it gives. An application adds its policies and binds them
to the presets by subclasses in the slots of :class:`AuthPolicies`::

    class AppPolicies(AuthPolicies):
        policy_banned_words = Slot(AppBannedWordsPolicy)
        preset_sign_up_nickname = Slot(AppSignUpNicknamePreset)
"""

__all__ = (
    "AuthChars",
    "AuthCharsConfig",
    "AuthCharsPolicy",
    "AuthHasValue",
    "AuthLengthConfig",
    "AuthLengthPolicy",
    "AuthPolicies",
    "AuthPolicyBinding",
    "AuthPolicyNotFoundError",
    "AuthPolicyPreset",
    "AuthPolicyViolationError",
    "AuthValueContext",
    "AuthValuePolicyPreset",
    "BaseAuthPolicy",
)

import typing as t

from ingots.puer import Slot, Unit

from .base import AuthPolicyBinding, BaseAuthPolicy
from .chars import AuthChars, AuthCharsConfig, AuthCharsPolicy
from .contexts import AuthHasValue, AuthValueContext
from .errors import AuthPolicyNotFoundError, AuthPolicyViolationError
from .length import AuthLengthConfig, AuthLengthPolicy
from .presets import AuthPolicyPreset, AuthValuePolicyPreset


class AuthPolicies(Unit):
    """
    The policies of the project, one a class, in the slots ``policy_*``, and
    their presets, in the slots ``preset_<flow>_<value>``.
    """

    policy_length = Slot(AuthLengthPolicy)
    policy_chars = Slot(AuthCharsPolicy)
    preset_sign_up_nickname = Slot(AuthValuePolicyPreset)
    preset_sign_up_password = Slot(AuthValuePolicyPreset)
    preset_sign_up_email = Slot(AuthValuePolicyPreset)

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
