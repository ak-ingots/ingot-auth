"""
The auth over HTTP, with the extra ``starlette``: the RPCs of the contract,
of :mod:`~ingot_auth.contrib.transports.contract`, transcoded to JSON by the annotations
``google.api.http`` of their methods, by ingot-starlette, no grpcio. An
endpoint a service, so that an application mounts those it serves in the
subtree of its API, the method it binds, with the policies of the auth and
the middleware telling the hash of the profile of the caller::

    class AppAuthEndpoint(StarletteEndpoint, Unit):
        metadata = Slot(AuthStarletteMetadataEndpoint)
        nickname = Slot(AuthStarletteNicknameEndpoint)
        sign_out = Slot(AuthStarletteSignOutEndpoint)

        @t.override
        def _iter_routes(self):
            yield from self.metadata.get_routes()
            yield from self.nickname.get_routes()
            yield from self.sign_out.get_routes()


    class AppApiUnit(StarletteApiUnit):
        auth = Slot(AppAuthEndpoint)

        @t.override
        def _iter_routes(self):
            yield Mount("/auth", routes=self.auth.get_routes())

        @t.override
        def _iter_middleware(self):
            yield Middleware(AuthStarletteProfileHashMiddleware)


    class AppStarletteErrorsUnit(AuthStarletteErrorsUnit):
        pass

A request bears the token of its session, ``Authorization: Bearer <token>``,
and runs for its caller; the metadata and the methods run for the anonymous
one, whatever it bears; the sign-out for the caller of the token, the
anonymous one of a token closed, expired or unknown, which signs out of
nothing: as over gRPC, the RPCs being the same.
"""

__all__ = (
    "PROFILE_HASH_STATE",
    "AuthStarletteEmailCodeEndpoint",
    "AuthStarletteErrorsUnit",
    "AuthStarletteMetadataEndpoint",
    "AuthStarletteNicknameEndpoint",
    "AuthStarletteOwnProfileEndpoint",
    "AuthStarletteOwnSessionsEndpoint",
    "AuthStarletteProfileHashMiddleware",
    "AuthStarletteSignInEndpoint",
    "AuthStarletteSignOutEndpoint",
    "AuthStarletteSignUpEndpoint",
    "BaseAuthStarletteEndpoint",
    "BaseAuthStarletteErrorPolicy",
    "StarletteAuthRpcContext",
)

from .base import PROFILE_HASH_STATE, BaseAuthStarletteEndpoint, StarletteAuthRpcContext
from .errors import AuthStarletteErrorsUnit, BaseAuthStarletteErrorPolicy
from .metadata import AuthStarletteMetadataEndpoint
from .methods import AuthStarletteEmailCodeEndpoint, AuthStarletteNicknameEndpoint
from .middleware import AuthStarletteProfileHashMiddleware
from .profiles import AuthStarletteOwnProfileEndpoint
from .sessions import AuthStarletteOwnSessionsEndpoint
from .sign_in import AuthStarletteSignInEndpoint
from .sign_out import AuthStarletteSignOutEndpoint
from .sign_up import AuthStarletteSignUpEndpoint
