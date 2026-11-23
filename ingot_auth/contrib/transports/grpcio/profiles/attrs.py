"""The servicer of the attributes."""

__all__ = ("AuthGrpcAttrsServicer",)

from .attrs_temp import (
    AuthGrpcAttrsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcAttrsServicer = AuthGrpcAttrsServicerTemp
