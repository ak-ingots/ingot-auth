"""The servicer of the members."""

__all__ = ("AuthGrpcMembersServicer",)

from .members_temp import (
    AuthGrpcMembersServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcMembersServicer = AuthGrpcMembersServicerTemp
