"""
The site over HTTP: the auth of a client of the web at ``/api/auth``, of
JSON alone, the hash of the profile of the caller in each response; the
pages of HTML of the site would come beside, at the root.
"""

import typing as t

from ingot_starlette.starlette import (
    StarletteApiUnit,
    StarletteEndpoint,
    StarletteUnit,
)
from ingots.puer import Slot, Unit
from starlette.middleware import Middleware
from starlette.routing import Mount

from ingot_auth.contrib.transports.starlette import (
    AuthStarletteEmailCodeEndpoint,
    AuthStarletteErrorsUnit,
    AuthStarletteMetadataEndpoint,
    AuthStarletteOwnProfileEndpoint,
    AuthStarletteOwnSessionsEndpoint,
    AuthStarletteProfileHashMiddleware,
    AuthStarletteSignInEndpoint,
    AuthStarletteSignOutEndpoint,
    AuthStarletteSignUpEndpoint,
)

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from starlette.routing import BaseRoute


class AppAuthEndpoint(StarletteEndpoint, Unit):
    """The auth a client of the web calls: what a visitor and a user do."""

    metadata = Slot(AuthStarletteMetadataEndpoint)
    email_code = Slot(AuthStarletteEmailCodeEndpoint)
    sign_up = Slot(AuthStarletteSignUpEndpoint)
    sign_in = Slot(AuthStarletteSignInEndpoint)
    sign_out = Slot(AuthStarletteSignOutEndpoint)
    own_sessions = Slot(AuthStarletteOwnSessionsEndpoint)
    own_profile = Slot(AuthStarletteOwnProfileEndpoint)

    @t.override
    def _iter_routes(self) -> "Iterator[BaseRoute]":
        for endpoint in (
            self.metadata,
            self.email_code,
            self.sign_up,
            self.sign_in,
            self.sign_out,
            self.own_sessions,
            self.own_profile,
        ):
            yield from endpoint.get_routes()


class AppApiUnit(StarletteApiUnit):
    auth = Slot(AppAuthEndpoint)

    @t.override
    def _iter_routes(self) -> "Iterator[BaseRoute]":
        yield Mount("/auth", routes=self.auth.get_routes())

    @t.override
    def _iter_middleware(self) -> "Iterator[Middleware]":
        yield Middleware(AuthStarletteProfileHashMiddleware)


class AppStarletteUnit(StarletteUnit):
    errors = Slot(AuthStarletteErrorsUnit)
    api = Slot(AppApiUnit)
