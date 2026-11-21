"""The RPCs of the methods, of no transport."""

__all__ = ("AuthNicknameRpcMixin", "BaseAuthMethodRpcMixin")

from .base import BaseAuthMethodRpcMixin
from .nickname import AuthNicknameRpcMixin
