"""
The policies: the rules a value a user types is checked against, each an
operation taking the part of its parameters its protocol tells, raising
:class:`AuthPolicyViolationError` with its name when the value breaks it.
The policies of a field of a flow are a group of a method, its slot
``policies_<flow>_<field>``, a :class:`~ingots.puer.Factories` of the type
the method gives, run together, each to its end, so that a client learns
every policy broken at once. The core gives the policies needing nothing
more, the length and the characters, configured by the ``CONFIG`` of their
class, which a subclass replaces::

    class AppNicknameLength(AuthLengthPolicy):
        CONFIG = AuthLengthConfig(min=3, max=20)

    class AppNicknameMethod(AuthNicknameMethod):
        policies_sign_up_nickname = AuthNicknameSignUpPolicies(AppNicknameLength)
"""

__all__ = (
    "AuthChars",
    "AuthCharsConfig",
    "AuthCharsPolicy",
    "AuthHasValue",
    "AuthLengthConfig",
    "AuthLengthPolicy",
    "AuthPolicyViolationError",
)

from .chars import AuthChars, AuthCharsConfig, AuthCharsPolicy
from .errors import AuthPolicyViolationError
from .length import AuthLengthConfig, AuthLengthPolicy
from .parameters import AuthHasValue
