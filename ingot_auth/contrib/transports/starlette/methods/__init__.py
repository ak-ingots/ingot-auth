"""The endpoints of the methods over HTTP."""

__all__ = (
    "AuthStarletteEmailCodeEndpoint",
    "AuthStarletteNicknameEndpoint",
    "AuthStarlettePasswordEndpoint",
)

from .email_code import AuthStarletteEmailCodeEndpoint
from .nickname import AuthStarletteNicknameEndpoint
from .password import AuthStarlettePasswordEndpoint
