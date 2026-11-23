"""The middleware telling the hash of the profile of the caller."""

__all__ = ("AuthStarletteProfileHashMiddleware",)

import typing as t

from ingot_auth.api import PROFILE_HASH_KEY
from .base import PROFILE_HASH_STATE

if t.TYPE_CHECKING:
    from starlette.types import ASGIApp, Message, Receive, Scope, Send


class AuthStarletteProfileHashMiddleware:
    """
    Tells in the header ``PROFILE_HASH_KEY`` of a response the hash of the
    profile of its caller, signed in, as the trailing metadata of gRPC does:
    a response refused tells it not. An application puts it in the
    middleware of the subtree of its API.
    """

    def __init__(self, app: "ASGIApp") -> None:
        self._app = app

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        async def send_hashed(message: "Message") -> None:
            profile_hash = scope.get("state", {}).get(PROFILE_HASH_STATE)
            if message["type"] == "http.response.start" and profile_hash:
                headers = list(message.get("headers", []))
                headers.append((PROFILE_HASH_KEY.encode(), profile_hash.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self._app(scope, receive, send_hashed)
