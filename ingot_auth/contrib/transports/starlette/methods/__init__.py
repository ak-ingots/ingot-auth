"""The endpoints of the methods over HTTP."""

__all__ = ("AuthStarletteEmailCodeEndpoint", "AuthStarletteNicknameEndpoint")

from .email_code import AuthStarletteEmailCodeEndpoint
from .nickname import AuthStarletteNicknameEndpoint
