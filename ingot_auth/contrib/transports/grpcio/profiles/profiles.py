"""The profiles themselves over gRPC: that of the caller, their values."""

__all__ = ("AuthGrpcProfilesServicer",)

from .profiles_temp import (
    AuthGrpcProfilesServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcProfilesServicer = AuthGrpcProfilesServicerTemp
