"""The servicer of the attributes of the sessions."""

__all__ = ("AuthGrpcSessionAttrsServicer",)

from .attrs_temp import (
    AuthGrpcSessionAttrsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcSessionAttrsServicer = AuthGrpcSessionAttrsServicerTemp
