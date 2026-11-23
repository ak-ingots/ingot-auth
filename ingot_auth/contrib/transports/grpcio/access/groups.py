"""The servicer of the groups."""

__all__ = ("AuthGrpcGroupsServicer",)

from .groups_temp import (
    AuthGrpcGroupsServicerTemp,
)

# the old names, aliases of the API till *Temp goes
AuthGrpcGroupsServicer = AuthGrpcGroupsServicerTemp
