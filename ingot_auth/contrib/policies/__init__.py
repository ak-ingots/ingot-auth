"""
The policies of a value that need what the core does not assume, a service
over the network: ``pwned``, a password leaked, by Pwned Passwords.
"""

__all__ = ("AuthPwnedConfig", "AuthPwnedPolicy")

from .pwned import AuthPwnedConfig, AuthPwnedPolicy
