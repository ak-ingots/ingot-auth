"""The sessions over gRPC: of the caller's own, of a profile."""

__all__ = (
    "CLOSE_REASONS",
    "AuthGrpcSessionsServicer",
)

from .sessions_temp import (
    CLOSE_REASONS,
    AuthGrpcSessionsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSessionsServicer = AuthGrpcSessionsServicerTemp
